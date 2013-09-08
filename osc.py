import lfsr

class Osc:

  def __init__(self, unit, periodreg):
    self.unit = unit
    self.index = 0
    self.value = None
    self.periodreg = periodreg

  def __call__(self):
    if not self.index:
      def applyperiod():
        self.limit = self.unit * self.periodreg.value
      self.value = self.nextvalue(self.value, applyperiod)
    self.index = (self.index + 1) % self.limit
    return self.value

class ToneOsc(Osc):

  scale = 16

  def __init__(self, periodreg):
    # Divide count by 2 so that the whole wave is 16:
    Osc.__init__(self, self.scale / 2, periodreg)

  def nextvalue(self, previous, applyperiod):
    if not previous: # Includes initial case.
      applyperiod()
      return 1
    else:
      return 0

class NoiseOsc(Osc):

  scale = 16

  def __init__(self, periodreg):
    # Halve the count so that the upper frequency bound is correct:
    Osc.__init__(self, self.scale / 2, periodreg)
    self.lfsr = lfsr.Lfsr(*lfsr.ym2149nzdegrees)

  def nextvalue(self, previous, applyperiod):
    applyperiod() # Unlike for tone, we can change period every half-wave.
    return self.lfsr()
