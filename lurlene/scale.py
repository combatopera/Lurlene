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

from .api import V

harmonicminor = V('0 2 3 5 7 8 11', step = 12, continuous = True)
major = V('0 2 4 5 7 9 11', step = 12, continuous = True)
naturalminor = V('0 2 3 5 7 8 10', step = 12, continuous = True)
octatonic = V('0 1 3 4 6 7 9 10', step = 12, continuous = True)
wholetone = V('0 2 4 6 8 10', step = 12, continuous = True)
