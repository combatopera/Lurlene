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

from . import E
from .iface import Config
from .util import Lazy
from .xtra import XTRA
from collections import defaultdict
from diapyr import types
import ast, bisect, logging, numpy as np, threading

log = logging.getLogger(__name__)

# FIXME: Do not transform names of class bases.
# FIXME: Update globalnames on the fly.
class Transform(ast.NodeTransformer):

    lazyname = '_lazy'

    def __init__(self, globalnames):
        self.lazycounts = defaultdict(lambda: 0)
        self.globalnames = globalnames

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load):
            return node
        name = node.id
        if name not in self.globalnames:
            return node
        self.lazycounts[name] += 1
        return ast.Call(ast.Name(self.lazyname, ast.Load()), [ast.Call(ast.Name('globals', ast.Load()), [], []), ast.Str(name)], [])

class Context:

    deleted = object()

    @types(Config)
    def __init__(self, config, sections = [(E(XTRA, '11/1'),)], xform = True):
        self._globals = self._slowglobals = dict(
            {Transform.lazyname: Lazy},
            __name__ = 'lurlene.context',
            tuning = config.tuning,
            mode = 1,
            speed = 16, # XXX: Needed when sections is empty?
            sections = sections,
        )
        self._snapshot = self._globals.copy()
        self._updates = self._slowupdates = {}
        self._cache = {}
        self._slowlock = threading.Lock()
        self._fastlock = threading.Lock()
        self._xform = xform

    def _update(self, text):
        addupdate = []
        delete = []
        with self._slowlock:
            with self._fastlock:
                self._globals = self._slowglobals.copy()
                self._updates = self._slowupdates.copy()
            before = self._slowglobals.copy()
            if self._xform:
                transform = Transform(self._slowglobals)
                code = compile(ast.fix_missing_locations(transform.visit(ast.parse(text))), '<string>', 'exec')
                if transform.lazycounts:
                    log.debug("Lazy: %s", ', '.join(f"""{n}{f"*{c}" if 1 != c else ''}""" for n, c in transform.lazycounts.items()))
            else:
                code = text
            exec(code, self._slowglobals) # XXX: Impact of modifying mutable objects?
            for name, value in self._slowglobals.items():
                if not (name in before and value is before[name]):
                    self._slowupdates[name] = value
                    addupdate.append(name)
            for name in before:
                if name not in self._slowglobals:
                    self._slowupdates[name] = self.deleted
                    delete.append(name)
            with self._fastlock:
                self._globals = self._slowglobals
                self._updates = self._slowupdates
        if addupdate:
            log.info("Add/update: %s", ', '.join(addupdate))
        if delete:
            log.info("Delete: %s", ', '.join(delete))
        if not (addupdate or delete):
            log.info('No change.')

    def _flip(self):
        if self._slowlock.acquire(False):
            try:
                with self._fastlock:
                    self._snapshot = self._globals.copy()
                    self._updates.clear()
            finally:
                self._slowlock.release()

    def __getattr__(self, name):
        with self._fastlock:
            # If the _globals value (or deleted) is due to _update, return _snapshot value (or deleted):
            try:
                value = self._globals[name]
            except KeyError:
                value = self.deleted
            if name in self._updates and value is self._updates[name]:
                try:
                    return self._snapshot[name]
                except KeyError:
                    raise AttributeError(name)
            if value is self.deleted:
                raise AttributeError(name)
            return value

    def _cachedproperty(f):
        name = f.__name__
        code = f.__code__
        params = code.co_varnames[1:code.co_argcount]
        def fget(self):
            args = [getattr(self, p) for p in params]
            try:
                cacheargs, value = self._cache[name]
                if all(x is y for x, y in zip(cacheargs, args)):
                    return value
            except KeyError:
                pass
            value = f(*[self] + args)
            self._cache[name] = args, value
            return value
        return property(fget)

    @_cachedproperty
    def _sections(self, speed, sections):
        return Sections(speed, sections)

class Sections:

    def __init__(self, speed, sections):
        self.sectionends = np.cumsum([speed * max(pattern.len for pattern in section) for section in sections])
        self.sections = sections

    @property
    def totalframecount(self):
        return self.sectionends[-1]

    def startframe(self, sectionindex):
        return self.sectionends[sectionindex - 1] if sectionindex else 0

    def sectionandframe(self, frameindex):
        localframe = frameindex % self.sectionends[-1]
        i = bisect.bisect(self.sectionends, localframe)
        return self.sections[i], localframe - self.startframe(i)
