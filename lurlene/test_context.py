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

from .context import Context
import unittest

class TestContext(unittest.TestCase):

    tuning = None

    def setUp(self):
        self.c = Context(self, (), False)

    def test_globals(self):
        self.c._update('''g = 5
def bump():
    global g
    g += 1''')
        self.c._flip()
        self.assertEqual(5, self.c.get('g'))
        self.c.get('bump')()
        self.assertEqual(6, self.c.get('g'))
        self.c._update('''foo = "bar"''')
        self.c._flip()
        self.assertEqual(6, self.c.get('g'))
        self.c.get('bump')()
        self.assertEqual(7, self.c.get('g'))

    def test_flip(self):
        self.c._update('''speed = 100''')
        self.assertEqual(16, self.c.get('speed'))
        self.c._flip()
        self.assertEqual(100, self.c.get('speed'))
        self.c._update('''del speed''')
        self.assertEqual(100, self.c.get('speed'))
        self.c._flip()
        with self.assertRaises(Context.NoSuchGlobalException) as cm:
            self.c.get('speed')
        self.assertEqual(('speed',), cm.exception.args)

    def test_flip2(self):
        self.c._update('''x = object()
y = object()
z = object()
sections = [x, y]''')
        self.assertEqual((), self.c.get('sections'))
        self.c._flip()
        s = self.c.get('sections')
        self.assertEqual([self.c.get('x'), self.c.get('y')], s)
        self.c._update('''sections = [y, z]''')
        self.assertIs(s, self.c.get('sections'))
        self.c._flip()
        self.assertEqual([self.c.get('y'), self.c.get('z')], self.c.get('sections'))
