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

from spectrogram import Silence
from pym2149.lc import E
from pym2149.pitch import Freq

class All:

    shape = 0x0e

    def on(self, chip):
        chip.toneflag = True
        chip.noiseflag = True
        chip.envflag = True
        chip.toneperiod = Freq(1000).toneperiod(chip._nomclock)
        chip.noiseperiod = Freq(5000).noiseperiod(chip._nomclock)
        chip.envperiod = Freq(1).envperiod(chip._nomclock, self.shape)
        if chip.envshape != self.shape:
            chip.envshape = self.shape

silence = E(Silence, '3')
A = E(All, '3'), silence, silence
sections = A,
speed = 25