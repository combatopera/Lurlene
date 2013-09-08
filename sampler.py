from __future__ import division
import math

class Sampler:

  def __init__(self, signal, ratio):
    self.signal = signal
    self.ratio = ratio
    self.index = -1
    self.pos = 0
    self.buf = []

  def getn(self):
    self.pos += self.ratio
    return int(math.ceil(self.pos - 1 - self.index))

  def load(self, n):
    if len(self.buf) < n:
      self.buf = [None] * n
    self.signal(self.buf, 0, n)
    self.last = self.buf[n - 1]
    self.index += n

class LastSampler(Sampler):

  def __call__(self, buf, bufstart, bufstop):
    for bufindex in xrange(bufstart, bufstop):
      self.load(self.getn())
      buf[bufindex] = self.last

class MeanSampler(Sampler):

  def __call__(self, buf, bufstart, bufstop):
    for bufindex in xrange(bufstart, bufstop):
      n = self.getn()
      if n:
        self.load(n)
        acc = 0
        for i in xrange(n):
          acc += self.buf[i]
        buf[bufindex] = acc / n
      else:
        buf[bufindex] = self.last
