# Copyright 2014 Andrzej Cichocki

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

import unittest
from aridipyimpl import Expressions, View, Fork

class TestFork(unittest.TestCase):

    def test_inheritedexpressionusescorrectcontext(self):
        expressions = Expressions()
        lines = ['woo = config.yay\n', '']
        readline = lambda: lines.pop(0)
        expressions.loadlines('whatever', readline)
        view = View(expressions)
        fork = Fork(view)
        view.yay = 'viewyay'
        self.assertEqual('viewyay', fork.woo)
        fork.yay = 'forkyay'
        self.assertEqual('forkyay', fork.woo)