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

from .transform import Interpreter
from unittest import TestCase

class TestTransform(TestCase):

    def test_newglobals(self):
        g = dict(a = 'A', b = 'B', L = lambda _, name: f"!{name}")
        exec('', g)
        snapshot = g.copy()
        Interpreter('L', g)('''x = a
y = b
z = y
w = x
class C: pass
ww = C
xx, yy = 100, 200
zz = yy''')
        self.assertEqual(dict(snapshot,
                x = '!a', y = '!b', z = '!y', w = '!x', C = g['C'], ww = '!C', xx = 100, yy = 200, zz = '!yy'), g)
