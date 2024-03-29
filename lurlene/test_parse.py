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

from .parse import VParse, EParse, BadWordException, _flatten, _readnumber
from .util import Lazy
from unittest import TestCase

class TestVParse(TestCase):

    @staticmethod
    def _perframes(segments):
        return [getattr(s, 'perframe', None) for s in segments.segments]

    def test_works(self):
        segments = VParse(float, 0, False).parse('1/1 2/1 .5/1', None)
        self.assertEqual([0, 1, 2], segments.frames)
        self.assertEqual(3, segments.len)
        self.assertEqual([1, 2, .5], [s.initial for s in segments.segments])
        self.assertEqual([1, -1.5, .5], self._perframes(segments))

    def test_widths(self):
        segments = VParse(float, 0, False).parse('1x/1 2x1/1 .5x2/.5', None) # Default value is 0.
        self.assertEqual([0, 1, 2, 3], segments.frames)
        self.assertEqual(3.5, segments.len)
        self.assertEqual([0, 1, 1, 2], [s.initial for s in segments.segments])
        self.assertEqual([1, None, 1, -4], self._perframes(segments))

    def test_slides(self):
        segments = VParse(float, 0, False).parse('5/.5 4/1 2x3/ 2/1', None) # Width of first word still implicitly 1.
        self.assertEqual([0, .5, 1, 2, 4], segments.frames)
        self.assertEqual(5, segments.len)
        self.assertEqual([5, 5, 4, 3, 2], [s.initial for s in segments.segments])
        self.assertEqual([None, -2, -1, -.5, 3], self._perframes(segments))

    def test_x(self):
        with self.assertRaises(BadWordException) as cm:
            VParse(float, 0, False).parse('x', None)
        self.assertEqual(('x',), cm.exception.args)

    def test_slash(self):
        segments = VParse(float, 0, False).parse('/ 7', None)
        self.assertEqual([0, 1], segments.frames)
        self.assertEqual(2, segments.len)
        self.assertEqual([0, 7], [s.initial for s in segments.segments])
        self.assertEqual([7, None], self._perframes(segments))

    def test_combo(self):
        segments = VParse(float, 0, False).parse('5x4/10 0/1', None)
        self.assertEqual([0, 5], segments.frames)
        self.assertEqual(6, segments.len)
        self.assertEqual([4, 0], [s.initial for s in segments.segments])
        self.assertEqual([-.4, 4], self._perframes(segments))

    def test_excess(self):
        segments = VParse(float, 0, False).parse('5/ 6/2 7', None)
        self.assertEqual([0, 1, 2], segments.frames)
        self.assertEqual(3, segments.len)
        self.assertEqual([5, 6, 7], [s.initial for s in segments.segments])
        self.assertEqual([1, .5, None], self._perframes(segments))

    def test_excess2(self):
        segments = VParse(float, 0, False).parse('5/2 6/', None)
        self.assertEqual([0, 1], segments.frames)
        self.assertEqual(2, segments.len)
        self.assertEqual([5, 6], [s.initial for s in segments.segments])
        self.assertEqual([.5, -1], self._perframes(segments))

    def test_halfnotes(self):
        segments = VParse(float, 0, False).parse('2.5x4/1 0/1', None) # Implicit slide is still 1.
        self.assertEqual([0, 1.5, 2.5], segments.frames)
        self.assertEqual(3.5, segments.len)
        self.assertEqual([4, 4, 0], [s.initial for s in segments.segments])
        self.assertEqual([None, -4, 4], self._perframes(segments))

class TestEParse(TestCase):

    def test_works(self):
        segments = EParse(None, None).parse('1 2 .5', None)
        self.assertEqual([0, 1, 3], segments.frames)
        self.assertEqual(3.5, segments.len)
        self.assertEqual([0, 1, 3], [s.relframe for s in segments.segments])
        self.assertEqual([None, None, None], [s.onframes for s in segments.segments])

    def test_works2(self):
        segments = EParse(None, None).parse('1 2 1/2', None)
        self.assertEqual([0, 1, 3], segments.frames)
        self.assertEqual(3.5, segments.len)
        self.assertEqual([0, 1, 3], [s.relframe for s in segments.segments])
        self.assertEqual([None, None, None], [s.onframes for s in segments.segments])

    def test_repeats(self):
        segments = EParse(None, None).parse('1x 2x3 3x2', None) # Default width is 1.
        self.assertEqual([0, 1, 4, 7, 9, 11], segments.frames)
        self.assertEqual(13, segments.len)
        self.assertEqual([0, 1, 4, 7, 9, 11], [s.relframe for s in segments.segments])
        self.assertEqual([None] * 6, [s.onframes for s in segments.segments])

    def test_badrepeat(self):
        with self.assertRaises(BadWordException) as cm:
            EParse(None, None).parse('.5x1', None)
        self.assertEqual(('.5x1',), cm.exception.args)
        with self.assertRaises(BadWordException) as cm:
            EParse(None, None).parse('-1x1', None)
        self.assertEqual(('-1x1',), cm.exception.args)
        # XXX: Allow as a way of commenting out?
        with self.assertRaises(BadWordException) as cm:
            EParse(None, None).parse('3 0x1 2', None)
        self.assertEqual(('0x1',), cm.exception.args)

    def test_noteoff(self):
        # In 'r.5' default width is 1, in '2r3' and 'r1.5' release is clamped to width:
        segments = EParse(None, None).parse('2r3 r.5 3r2 r1.5', None)
        self.assertEqual([0, 2, 2.5, 3, 4, 6], segments.frames)
        self.assertEqual(7, segments.len)
        self.assertEqual([0, 2, 2.5, 3, 4, 6], [s.relframe for s in segments.segments])
        self.assertEqual([0, None, .5, None, 1, 0], [s.onframes for s in segments.segments])

    def test_noteoff2(self):
        segments = EParse(None, None).parse('2r3 r1/2 3r2 r3/2', None)
        self.assertEqual([0, 2, 2.5, 3, 4, 6], segments.frames)
        self.assertEqual(7, segments.len)
        self.assertEqual([0, 2, 2.5, 3, 4, 6], [s.relframe for s in segments.segments])
        self.assertEqual([0, None, .5, None, 1, 0], [s.onframes for s in segments.segments])

    def test_rests(self):
        segments = EParse(None, None).parse('2z .5z z', None)
        self.assertEqual([0, 2, 2.5], segments.frames)
        self.assertEqual(3.5, segments.len)
        self.assertEqual([0, 2, 2.5], [s.relframe for s in segments.segments])
        self.assertEqual([None, None, None], [s.onframes for s in segments.segments])

    def test_rests2(self):
        segments = EParse(None, None).parse('2z 1/2z z', None)
        self.assertEqual([0, 2, 2.5], segments.frames)
        self.assertEqual(3.5, segments.len)
        self.assertEqual([0, 2, 2.5], [s.relframe for s in segments.segments])
        self.assertEqual([None, None, None], [s.onframes for s in segments.segments])

class TestFlatten(TestCase):

    def test_lazy(self):
        g = dict(a = 'x', b = 'yy', c = 'z')
        self.assertEqual('x yy z', _flatten([[[Lazy(g, 'a')], Lazy(g, 'b')], Lazy(g, 'c')]))

class TestReadNumber(TestCase):

    def test_works(self):
        self.assertEqual(.5, _readnumber('.5', None))
        self.assertEqual(-.5, _readnumber('-.5', None))
        self.assertEqual(.5, _readnumber('1/2', None))
        self.assertEqual(-.5, _readnumber('-1/2', None))
        self.assertEqual(.5, _readnumber('/2', None))
        self.assertEqual(-.5, _readnumber('-/2', None))
        self.assertEqual(100, _readnumber(None, 100))
        self.assertEqual(100, _readnumber('', 100))
