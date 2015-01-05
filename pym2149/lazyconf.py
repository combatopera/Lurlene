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

import re, logging

log = logging.getLogger(__name__)

class Expression:

    def __init__(self, head, code, name):
        self.head = head
        self.code = code
        self.name = name

    def __call__(self, view):
        g = dict(config = view)
        exec (self.head, g)
        exec (self.code, g)
        return g[self.name]

class View:

    def __init__(self, loader):
        self.loader = loader

    def __getattr__(self, name):
        return self.loader.expressions[name](self)

class Loader:

    assignment = re.compile(r'^([^\s]+)\s*=')

    def __init__(self):
        self.expressions = {}

    def load(self, path):
        f = open(path)
        try:
            head = []
            line = f.readline()
            while line and self.assignment.search(line) is None:
                head.append(line)
                line = f.readline()
            tocode = lambda block: compile(block, '<string>', 'exec')
            log.debug("[%s] Header is first %s lines.", path, len(head))
            head = tocode(''.join(head))
            while line:
                m = self.assignment.search(line)
                if m is not None:
                    name = m.group(1)
                    self.expressions[name] = Expression(head, tocode(line), name)
                line = f.readline()
        finally:
            f.close()
