# Copyright 2014, 2018, 2019 Andrzej Cichocki

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

from .pitch import Pitch
from .program import FX
from .const import midichannelcount
from .mediation import Mediation
from .iface import Chip, Config
from .config import ConfigSubscription, ConfigName
from .util import singleton
from diapyr import types, DI
from contextlib import contextmanager
import logging

log = logging.getLogger(__name__)

@singleton
class NullChanNote:

    def programornone(self): pass

    def getpan(self): return 0

    def update(self, frame): pass

class ChanNote:

    def __init__(self, onframe, program, nomclock, chip, chipindex, midinote, voladj, fx):
        self.program = program
        with self._guard():
            self.note = program(nomclock, chip, chipindex, Pitch(midinote), voladj, fx)
        self.onframe = onframe
        self.chip = chip
        self.chipindex = chipindex
        self.midinote = midinote
        self.fx = fx
        self.offframe = None

    def programornone(self):
        return self.program

    def getpan(self):
        return self.fx.normpan()

    def update(self, frame):
        with self._guard():
            self._update(frame)

    @contextmanager
    def _guard(self):
        program = self.program
        try:
            yield
        except Exception:
            log.exception("%s failed:", program.__name__)
            self.update = lambda *args: None # Freeze this note.

    def _callnoteon(self):
        self.chip.flagsoff(self.chipindex) # Make it so that the impl only has to switch things on. TODO LATER: Not all notes will want this, e.g. overlay hihats or buzzer-combining tone.
        self.note.noteon()

    def _update(self, frame):
        if self.offframe is None:
            f = frame - self.onframe
            if not f:
                self._callnoteon()
            self.note.noteonframe(f) # May never be called, so noteoff/noteoffframe should not rely on side-effects.
        else:
            if self.onframe == self.offframe:
                self._callnoteon()
            f = frame - self.offframe
            if not f:
                self.note.onframes = self.offframe - self.onframe
                self.note.noteoff()
            self.note.noteoffframe(f)

class Channel:

    def __init__(self, config, chipindex, chip):
        self.nomclock = config.nominalclock
        neutralvel = config.neutralvelocity
        velperlevel = config.velocityperlevel
        self.tovoladj = lambda vel: (vel - neutralvel + velperlevel // 2) // velperlevel
        self.chipindex = chipindex
        self.chip = chip
        self.channote = NullChanNote

    def programstr(self):
        program = self.channote.programornone()
        if program is not None:
            return program.__name__

    def newnote(self, frame, program, midinote, vel, fx):
        self.channote = ChanNote(frame, program, self.nomclock, self.chip, self.chipindex, midinote, self.tovoladj(vel), fx)

    def noteoff(self, frame):
        self.channote.offframe = frame

    def update(self, frame):
        self.channote.update(frame)

    def getpan(self):
        return self.channote.getpan()

    def __str__(self):
        return chr(ord('A') + self.chipindex)

class ControlPair:

    def __init__(self, binaryzero, flush, shift):
        self.binary = self.binaryzero = binaryzero
        self.flush = flush
        self.shift = shift

    def install(self, d, msbindex):
        d[msbindex] = self.setmsb
        d[msbindex + 0x20] = self.setlsb

    def setmsb(self, midichan, msb):
        self.binary = (msb << 7) | (self.binary & 0x7f)
        self.flush(midichan, (self.binary - self.binaryzero) >> self.shift)

    def setlsb(self, midichan, lsb):
        self.binary = (self.binary & (0x7f << 7)) | lsb
        self.flush(midichan, (self.binary - self.binaryzero) >> self.shift)

class Channels:

    @classmethod
    def configure(cls, di):
        di.add(cls)
        di.add(ChannelsConfigSubscription)

    @types(Config, Chip, Mediation)
    def __init__(self, config, chip, mediation):
        self.channels = [Channel(config, i, chip) for i in range(config.chipchannels)]
        self.midichantoprogram = dict(config.midichanneltoprogram) # Copy as we will be changing it.
        self.slidemidichans = set(config.slidechannels)
        self.fxfactory = lambda midichan: FX(config, midichan in self.slidemidichans)
        self.midichantofx = {c: self.fxfactory(c) for c in range(config.midichannelbase, config.midichannelbase + midichannelcount)}
        self.mediation = mediation
        self.zerovelisnoteoffmidichans = set(config.zerovelocityisnoteoffchannels)
        self.monophonicmidichans = set(config.monophonicchannels)
        self.controllers = {}
        def flush(midichan, value):
            self.midichantofx[midichan].modulation.set(value)
        ControlPair(0, flush, 0).install(self.controllers, 0x01)
        def flush(midichan, value):
            self.midichantofx[midichan].pan.set(value)
        ControlPair(0x2000, flush, 0).install(self.controllers, 0x0a)
        self.prevtext = None
        self.frameindex = 0

    def reconfigure(self, config):
        self.midiprograms = config.midiprograms

    def _getfx(self, midichan):
        try:
            fx = self.midichantofx[midichan]
        except KeyError:
            self.midichantofx[midichan] = fx = self.fxfactory(midichan)
        return fx

    def noteon(self, midichan, midinote, vel):
        if (not vel) and midichan in self.zerovelisnoteoffmidichans: # TODO: This is normal, confirm midi spec.
            return self.noteoff(midichan, midinote, vel)
        if midichan in self.monophonicmidichans:
            for mn in range(0x80):
                self.noteoff(midichan, mn, 0)
        # XXX: Keep owner program for logging?
        program = self.midiprograms[self.midichantoprogram[midichan]].programformidinote(midinote)
        fx = self._getfx(midichan)
        chipchan = self.mediation.acquirechipchan(midichan, midinote, self.frameindex)
        channel = self.channels[chipchan]
        if midichan in self.slidemidichans:
            fx.bend.value = 0 # Leave target and rate as-is. Note race with midi instant pitch bend (fine part 0).
        channel.newnote(self.frameindex, program, midinote, vel, fx)
        return channel

    def noteoff(self, midichan, midinote, vel): # XXX: Use vel?
        chipchan = self.mediation.releasechipchan(midichan, midinote)
        if chipchan is not None:
            channel = self.channels[chipchan]
            if midinote == channel.channote.midinote:
                channel.noteoff(self.frameindex)
                return channel

    def pitchbend(self, midichan, bend):
        self.midichantofx[midichan].bend.set(bend)

    def controlchange(self, midichan, controller, value):
        if controller in self.controllers:
            self.controllers[controller](midichan, value)

    def programchange(self, midichan, program):
        self.midichantoprogram[midichan] = program

    def updateall(self):
        text = ' | '.join("%s@%s" % (c.programstr(), self.mediation.currentmidichans(c.chipindex)) for c in self.channels)
        if text != self.prevtext:
            log.debug(text)
            self.prevtext = text
        for channel in self.channels:
            channel.update(self.frameindex)

    def closeframe(self):
        for fx in self.midichantofx.values():
            fx.applyrates()
        self.frameindex += 1

    def getpans(self):
        for c in self.channels:
            yield c.getpan()

    def __str__(self):
        return ', '.join("%s -> %s" % (midichan, self.midiprograms[program]) for midichan, program in sorted(self.midichantoprogram.items()))

class ChannelsConfigSubscription(ConfigSubscription):

    @types(ConfigName, DI, Channels)
    def __init__(self, configname, di, channels):
        super().__init__(configname, di, channels.reconfigure)
