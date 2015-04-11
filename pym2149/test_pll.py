#!/usr/bin/env python

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

from __future__ import division
from collections import namedtuple
from pll import PLL
import unittest, time

dp = 6

class Event:

    def __init__(self, eventtime):
        self.eventtime = eventtime

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, round(self.eventtime, dp))

class TestPLL(unittest.TestCase):

    updaterate = 50
    updateperiod = 1 / updaterate
    alpha = .2

    def doit(self, positionshift, *offsetlists):
        pll = PLL(namedtuple('Config', 'updaterate pllalpha')(self.updaterate, self.alpha))
        pll.start()
        eventlists = []
        for u, offsets in enumerate(offsetlists):
            updatetime = pll.mark + self.updateperiod * (u + .5)
            eventlists.append([Event(updatetime + offset) for offset in offsets])
        updates = []
        for events in eventlists:
            for event in events:
                while pll.exclusivewindowend <= event.eventtime:
                    updates.append(pll.takeupdate(pll.exclusivewindowend))
                pll.event(event, eventtime = event.eventtime)
        ewe = pll.exclusivewindowend
        updates.append(pll.takeupdate(ewe))
        self.assertEqual(eventlists, updates)
        self.assertEqual(positionshift, round(ewe - (pll.mark + self.updateperiod * len(eventlists)), dp))

    def test_0perfecttiming(self):
        self.doit(0,
            [0],
            [0],
            [],
            [0],
            [0, 0],
            [0],
        )

    def test_1consistentlylate(self):
        self.doit(.005,
            [.005],
            [.005],
            [],
            [.005],
            [.005, .005],
            [.005],
        )

    def test_2consistentlyearly(self):
        self.doit(-.005,
            [-.005],
            [-.005],
            [],
            [-.005],
            [-.005, -.005],
            [-.005],
        )

    def test_3hundredthgranularity(self):
        self.doit(-0.004894,
            [0],
            [-.009],
            [0],
            [-.01],
            [-.01],
            [0],
            [-.01],
            [0],
        )

    def test_5hundredthgranularityaltshift(self):
        self.doit(0.004779,
            [.009],
            [0],
            [.01],
            [0],
            [0],
            [.01],
            [0],
            [.01],
        )

if '__main__' == __name__:
    unittest.main()
