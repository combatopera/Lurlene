from pym2149.lc import V, D, E, major
from pym2149.pitches import F4

class Bass:

    envshape = 0x0a
    envpitches = D('2x++,+'), D('2x++ 5x+,1')

    def on(self, frame, chip, degree, slap = V('0'), hard = V('0')):
        chip.fixedlevel = 15
        chip.noiseflag = False
        chip.toneflag = True
        chip.tonepitch = chip.topitch(degree[frame])
        chip.envflag = True
        if frame < 1 and hard[frame]:
            chip.envshape = self.envshape
        chip.envpitch = chip.topitch((slap[frame].pick(self.envpitches) + degree)[frame])

class Kick:

    level = V('13 3x15 13//3 10')
    nf = V('1,0')
    tf = V('0,1')
    pitch = V('2x47 43 40 32 3x24')

    def on(self, frame, chip):
        if frame < 8:
            chip.fixedlevel = self.level[frame]
            chip.noiseflag = self.nf[frame]
            chip.toneflag = self.tf[frame]
            chip.noiseperiod = 7
            chip.tonepitch = self.pitch[frame]

class Snare:

    level = V('4x13 11 10'), V('4x15 13 11')
    nf = V('1 3x,1')
    np = V('17,13')
    tf = V('4x1,0')
    pitch = V('64 60 57 55')

    def on(self, frame, chip, vel = V('1')):
        if frame < 6:
            chip.fixedlevel = vel[frame].pick(self.level)[frame]
            chip.noiseflag = self.nf[frame]
            chip.noiseperiod = self.np[frame]
            chip.toneflag = self.tf[frame]
            chip.tonepitch = self.pitch[frame]

class Arp:

    levels = V('10'), V('14//15 18x9 8 2x7 6//24,0')
    chords = D('1 3 5').inversions()
    vib = V('15.5x,/3 -.4/6 .4/3')

    def on(self, frame, chip, degree, inv = V('0'), vel = V('1')):
        chip.fixedlevel = vel[frame].pick(self.levels)[frame]
        chip.noiseflag = False
        chip.toneflag = True
        chip.tonepitch = chip.topitch((degree + inv[frame].pick(self.chords))[frame]) + self.vib[frame]

bass1 = E(Bass, 2 * ['/.5 /.5 .5 /.5 /.5 .5 /.5 .5 1.5/1|/.5 /.5 .5 /.5 /.5 .5 /.5 4x.5'],
        degree = D('--') + D('2- 2 .5x 2 1.5x2- 2 .5x 1.5x2|2- 2 .5x 2 1.5x2- 2 .5x .5x2 .5x6- .5x'),
        hard = V('1,0'))
bass2 = E(Bass, '/.5 /.5 .5 /.5 /.5 .5 /.5 4x.5|/.5 /.5 .5 /.5 9x.5',
        degree = D('---') + D('2 2+ .5x+ 2+ 1.5x2 2+ .5x+ .5x2+ .5x5- .5x5|6- 6 .5x5 6 6- .5x6 .5x7- .5x7 .5x .5x+ .5x# .5x#+'))
bass3 = E(Bass, '32x.5',
        degree = D('---') + D(['2 2+'] * 5, '3 3+ 4 4+ 5- 5', ['6- 6'] * 5, '7- 7 1 + # #+').of(.5),
        slap = V(['0 1'] * 7, '2x').of(.5))
bass3a = E(Bass, ['.75/.75 .25'] * 7, '/1',
        degree = D('---') + D('5x2 3 2x4|5x6- 7- 2x'))
kick1 = E(Kick, '2')
kick2 = E(Kick, '12x .5/.5 .25 .75 2.5')
snare2 = E(Snare, '/13 1 .25 .5 .25 .5 2x.25',
        vel = V('14.25x1 .75x .5x1 .25x .25x1'))
snare3 = E(Snare, '/1 3x2 .75 1.25/1 2x2 1.25 .75 .5 2x.25')
arp1 = E(Arp, '1.5 6.5',
        degree = D('1.5x 6.5x4 1.5x5 6.5x'),
        inv = V('1.5x2 6.5x1 1.5x 6.5x2'))
arp4 = E(Arp, '.25/.25 /.5 .25 .75/.5 7x/.5 .25 .75/.5 3x/.5 1.25/.75 2x.75/.5',
        degree = D('1.5x 6.5x4 1.5x5 6.5x'),
        inv = V('1.5x2 6.5x1 1.5x 6.5x2'),
        vel = V('0'))
A = bass1, kick1, arp1
B = bass2, kick2 & snare2, arp1
C = bass3 * 2, kick1 & snare3 & bass3a, arp1
F = bass3, kick1 & snare3 & bass3a & arp4
sections = A, B, C, F
scale = major
tonic = F4
speed = 20