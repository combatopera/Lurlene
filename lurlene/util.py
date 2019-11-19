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

from contextlib import contextmanager
import threading, logging

log = logging.getLogger(__name__)
local = threading.local()
deleted = object()

@contextmanager
def threadlocals(**kwargs):
    old = {name: getattr(local, name) if hasattr(local, name) else deleted for name in kwargs}
    for name, value in kwargs.items():
        setattr(local, name, value)
    try:
        yield
    finally:
        for name, value in old.items():
            if value is deleted:
                delattr(local, name)
            else:
                setattr(local, name, value)

def outerzip(*iterables):
    iterators = [iter(i) for i in iterables]
    def g():
        nonlocal running
        for i in iterators:
            try:
                yield next(i)
            except StopIteration:
                running -= 1
                yield
    n = len(iterators)
    while True:
        running = n
        values = tuple(g())
        if not running:
            break
        yield values

@contextmanager
def catch(obj, *logargs):
    if not hasattr(obj, '_onfire'):
        obj._onfire = False
    try:
        yield
        obj._onfire = False
    except Exception:
        if not obj._onfire: # TODO: Show error if it has changed.
            log.exception(*logargs)
            obj._onfire = True