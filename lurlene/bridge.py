# Copyright 2019 Andrzej Cichocki

# This file is part of Lurlene.
#
# Lurlene is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lurlene is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lurlene.  If not, see <http://www.gnu.org/licenses/>.

from .context import Sections, Context
from .iface import Config
from .util import threadlocals, catch
from diapyr import types
from diapyr.util import innerclass, singleton
from functools import partial
import logging, bisect, difflib

log = logging.getLogger(__name__)

class NoSuchSectionException(Exception): pass

class LiveCodingBridge:

    bias = .5 # TODO: Make configurable for predictable swing in odd speed case.

    @types(Config, Context)
    def __init__(self, config, context):
        self.loop = not config.ignoreloop
        self.sectionname = config.section
        self.context = context

    @property
    def pianorollheight(self):
        return self.context.speed

    @innerclass
    class Session:

        def __init__(self, chips):
            self.chips = chips

        def _quiet(self):
            for proxy in self.chips:
                proxy.noiseflag = False
                proxy.toneflag = False
                proxy.envflag = False
                proxy.level = 0

        def _step(self, speed, section, frame):
            self._quiet()
            for proxy, pattern in zip(self.chips, section):
                with catch(proxy, "Channel %s update failed:", proxy._letter):
                    pattern.apply(speed, frame, proxy)

    def _initialframe(self):
        if self.sectionname is None:
            return 0
        section = getattr(self.context, self.sectionname)
        try:
            i = self.context.sections.index(section)
        except ValueError:
            raise NoSuchSectionException(self.sectionname)
        return self.context._sections.startframe(i)

    def frames(self, chips):
        session = self.Session(chips)
        frameindex = self._initialframe() + self.bias
        with threadlocals(context = self.context):
            while self.loop or frameindex < self.context._sections.totalframecount:
                oldspeed = self.context.speed
                oldsections = self.context.sections
                frame = session._quiet
                if self.context._sections.totalframecount: # Otherwise freeze until there is something to play.
                    with catch(session, 'Failed to prepare a frame:'):
                        frame = partial(session._step, self.context.speed, *self.context._sections.sectionandframe(frameindex))
                        frameindex += 1
                frame()
                yield
                self.context._flip()
                if oldspeed != self.context.speed:
                    frameindex = (frameindex - self.bias) / oldspeed * self.context.speed + self.bias
                if oldsections != self.context.sections:
                    frameindex = self._adjustframeindex(Sections(self.context.speed, oldsections), frameindex)

    def _adjustframeindex(self, oldsections, frameindex):
        baseframe = (frameindex // oldsections.totalframecount) * self.context._sections.totalframecount
        localframe = frameindex % oldsections.totalframecount
        oldsectionindex = bisect.bisect(oldsections.sectionends, localframe)
        sectionframe = localframe - oldsections.startframe(oldsectionindex)
        opcodes = difflib.SequenceMatcher(a = oldsections.sections, b = self.context.sections).get_opcodes()
        @singleton
        def sectionindexandframe():
            for tag, i1, i2, j1, j2 in opcodes:
                if 'equal' == tag and i1 <= oldsectionindex and oldsectionindex < i2:
                    return j1 + oldsectionindex - i1, sectionframe
            oldsection = oldsections.sections[oldsectionindex]
            for tag, i1, i2, j1, j2 in opcodes:
                if 'insert' == tag and oldsection in self.context.sections[j1:j2]:
                    return j1 + self.context.sections[j1:j2].index(oldsection), sectionframe
            for tag, i1, i2, j1, j2 in opcodes:
                if tag in {'delete', 'replace'} and i1 <= oldsectionindex and oldsectionindex < i2:
                    return j1, 0
        return baseframe + (0 if sectionindexandframe is None else (self.context._sections.startframe(sectionindexandframe[0]) + sectionindexandframe[1]))