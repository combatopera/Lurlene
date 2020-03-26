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

from .transform import Transform
from unittest import TestCase
import ast

class TestTransform(TestCase):

    def test_newglobals(self):
        g = dict(a = 'A')
        t = Transform('L', g)
        lines = t._transform('''x = a
y = b
z = y
w = x''').body
        self.assertEqual(dict(a = 'A'), g)
        self.assertIsInstance(lines.pop(0).value, ast.Call)
        self.assertIsInstance(lines.pop(0).value, ast.Name)
        self.assertIsInstance(lines.pop(0).value, ast.Call)
        self.assertIsInstance(lines.pop(0).value, ast.Call)
        self.assertFalse(lines)
