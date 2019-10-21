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

from spectrogram import silence
from .lc import E

class Tri650:

    shape = 0x0a

    def on(self, chip):
        chip.envflag = True
        if chip.envshape != self.shape:
            chip.envshape = self.shape
        chip.envfreq = 650

sections = [[E(Tri650, '1.5'), silence, silence]]
speed = 50
