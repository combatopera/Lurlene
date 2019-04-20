#!/usr/bin/env pyven

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

from pym2149.initlogging import logging
from pym2149 import foxdot
from pym2149.portaudio import PortAudioClient, PortAudioStream
from pym2149.midi import EventPump
from pym2149.config import ConfigName
from pym2149.channels import Channels
from pym2149.boot import boot
from pym2149.util import awaitinterrupt
from pym2149.pll import PLL
from pym2149.timerimpl import SyncTimer
from pym2149.foxdotlib import Delay
from diapyr.start import Started

del logging

def main():
    config, di = boot(ConfigName('--session', '--window', name = 'foxdot'))
    try:
        di.add(Delay)
        di.add(PLL) # XXX: Can we crank up the updaterate instead? It's 44100/64=689 in SC.
        di.add(PortAudioClient)
        di.add(config.mediation)
        Channels.configure(di)
        di.add(SyncTimer)
        foxdot.configure(di)
        di.add(PortAudioStream)
        di.add(EventPump)
        di.all(Started)
        awaitinterrupt(config)
    finally:
        di.discardall()

if '__main__' == __name__:
    main()