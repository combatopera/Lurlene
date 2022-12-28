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

from . import api, scale
from .util import All as __all__

__all__ = __all__(globals())
__all__.update([name, getattr(api, name)] for name in ['D', 'E', 'topitch', 'unit', 'V'])
__all__.update([name, getattr(scale, name)] for name in ['harmonicminor', 'major', 'naturalminor', 'octatonic', 'wholetone'])
del api, scale
