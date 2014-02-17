#!/usr/bin/env python

import unittest
from mix import IdealMixer, Multiplexer
from nod import BufNode, Block, Container
from buf import NullBuf

class Counter(BufNode):

  def __init__(self, x = 0):
    BufNode.__init__(self, int)
    self.x = x

  def callimpl(self):
    for frameindex in xrange(self.block.framecount):
      self.blockbuf.fillpart(frameindex, frameindex + 1, self.x)
      self.x += 1

class TestIdealMixer(unittest.TestCase):

  def expect(self, m, values, actual):
    self.assertEqual(len(values), len(actual))
    for i in xrange(len(values)):
      self.assertAlmostEqual(m.datum - values[i], actual.buf[i])

  def test_works(self):
    m = IdealMixer(Container([Counter(10), Counter()]))
    self.expect(m, [10, 12, 14, 16, 18], m.call(Block(5)))
    # Check the buffer is actually cleared first:
    self.expect(m, [20, 22, 24, 26, 28], m.call(Block(5)))

  def test_masked(self):
    upstream = Counter(10), Counter()
    m = IdealMixer(Container(upstream))
    self.assertEqual(NullBuf, m(Block(5), True))
    for n in upstream:
      self.assertEqual(NullBuf, n.result)

class TestMultiplexer(unittest.TestCase):

  def test_works(self):
    a = Counter()
    b = Counter(10)
    c = Counter(30)
    m = Multiplexer(a, b, c)
    self.assertEqual([0, 10, 30, 1, 11, 31, 2, 12, 32, 3, 13, 33, 4, 14, 34], m.call(Block(5)).tolist())

if __name__ == '__main__':
  unittest.main()
