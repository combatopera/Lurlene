# Copyright 2014 Andrzej Cichocki

# This file is part of pym2149.
#
# pym2149 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pym2149 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pym2149.  If not, see <http://www.gnu.org/licenses/>.

from pym2149.util import singleton
import logging

log = logging.getLogger(__name__)

@singleton
class nullnote:

  def noteon(self, chip, chan):
    pass # Flags are turned off by NoteAction.

  def update(self, chip, chan, frameindex):
    pass

class NoteAction:

  def __init__(self, note):
    self.note = note

  def onnoteornone(self, chip, chan):
    # The note needn't know all the chip's features, so turn them off first:
    chip.flagsoff(chan)
    self.note.noteon(chip, chan)
    return self.note

@singleton
class sustainaction:

  def onnoteornone(self, chip, chan):
    pass

def getorlast(v, i):
  try:
    return v[i]
  except IndexError:
    return v[-1]

class Orc(dict):

  def add(self, cls, key = None):
    if key is None:
      key = cls.__name__[0]
    if key in self:
      raise Exception("Key already in use: %s" % key)
    self[key] = cls
    return cls

class Play:

  voidaction = NoteAction(nullnote)

  def __init__(self, orc, timer):
    self.orc = orc
    self.timer = timer

  def __call__(self, beatsperbar, beats, *args, **kwargs):
    frames = []
    paramindex = 0
    for char in beats:
      if '.' == char:
        action = sustainaction
      elif '-' == char:
        action = self.voidaction
      else:
        nargs = [getorlast(v, paramindex) for v in args]
        nkwargs = dict([k, getorlast(v, paramindex)] for k, v in kwargs.iteritems())
        noteclass = self.orc[char]
        try:
          note = noteclass(self.orc, *nargs, **nkwargs)
        except:
          log.info("Note class that errored: %s", noteclass)
          raise
        action = NoteAction(note)
        paramindex += 1
      frames.append(action)
      b, = self.timer.blocksforperiod(beatsperbar)
      for _ in xrange(b.framecount - 1):
        frames.append(sustainaction)
    return frames

class Updater:

  def __init__(self, onnote, chip, chan, frameindex):
    self.onnote = onnote
    self.chip = chip
    self.chan = chan
    self.frameindex = frameindex

  def update(self, frameindex):
    self.onnote.update(self.chip, self.chan, frameindex - self.frameindex)

@singleton
class voidupdater:

  def update(self, frameindex):
    pass
