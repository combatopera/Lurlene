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

from .parse import concat, EParse, Program, rebase, Script, StepScript, vector, VParse
from .util import local

def V(*script, step = 0, continuous = False):
    return concat(lambda *args: StepScript(*args, step), VParse(float, step, continuous), script, {})

def D(*script):
    return concat(Script, VParse(vector, 0, False), script, {})

def E(cls, *script, initargs = (), **kwargs):
    namespace = object()
    kwargs = {(namespace, name): value for name, value in kwargs.items()}
    return concat(Script, EParse(Program(cls, initargs), namespace), script, kwargs)

unit = E(None, 'z')

def topitch(degree):
    c = local.context
    return _topitch(c.get('scale'), c.get('mode'), c.get('tonic'), degree)

def _topitch(scale, mode, tonic, degree):
    mode = rebase(mode)
    return tonic - scale[mode] + float((scale << mode)[degree[0] * scale.len + degree[1]] + degree[2])
