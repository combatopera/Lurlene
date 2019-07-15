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

from .iface import Chip, Stream, Unit, Prerecorded, Config
from .timer import Timer
from diapyr import types
import logging, math

log = logging.getLogger(__name__)
refreshrate = 50 # Authentic period.

class BadCommandException(Exception): pass

class Bytecode(Prerecorded):

    def __init__(self, bytes):
        self.bytes = bytes

@types(Config, Bytecode, Chip, Timer, Stream, this = Unit)
def dosound(config, bytecode, chip, timer, stream):
    extraseconds = config.dosoundextraseconds
    for _ in _dosound(bytecode.bytes, chip):
        for b in timer.blocksforperiod(refreshrate):
            stream.call(b)
    if extraseconds:
        n = math.ceil(extraseconds * refreshrate)
        log.info("Streaming %.3f extra seconds.", n / refreshrate)
        for _ in range(n):
            for b in timer.blocksforperiod(refreshrate):
                stream.call(b)
    stream.flush()

def _dosound(bytecode, chip):
    def g():
        for b in bytecode:
            yield b & 0xff # It's supposed to be bytecode.
    g = g()
    while True:
        ctrl = next(g)
        if ctrl <= 0xF:
            chip.R[ctrl].value = next(g)
        elif 0x80 == ctrl:
            softreg = next(g)
        elif 0x81 == ctrl:
            targetreg = chip.R[next(g)]
            adjust = next(g)
            if adjust >= 0x80:
                adjust -= 0x100 # Convert back to signed.
            last = next(g)
            while True:
                softreg += adjust # Yes, this is done up-front.
                # The real thing simply uses the truncation on overflow:
                targetreg.value = softreg
                yield
                # That's right, if we skip past it we loop forever:
                if last == softreg:
                    break
        elif issleepcommand(ctrl):
            ticks = next(g)
            if not ticks:
                break
            ticks += 1 # Apparently!
            for _ in range(ticks):
                yield
        else:
            raise BadCommandException(ctrl)

def issleepcommand(ctrl):
    return ctrl >= 0x82
