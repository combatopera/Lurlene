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

from collections import defaultdict
import ast, logging

log = logging.getLogger(__name__)

# FIXME: Do not transform names of class bases.
# FIXME: Update globalnames on the fly.
class Transform(ast.NodeTransformer):

    def __init__(self, lazyname, globalnames):
        self.lazyname = lazyname
        self.globalnames = globalnames

    def _transform(self, text):
        self.lazycounts = defaultdict(lambda: 0)
        tree = ast.fix_missing_locations(self.visit(ast.parse(text)))
        if self.lazycounts:
            log.debug("Lazy: %s", ', '.join(f"""{n}{f"*{c}" if 1 != c else ''}""" for n, c in self.lazycounts.items()))
        return tree

    def transform(self, text):
        return compile(self._transform(text), '<string>', 'exec')

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load):
            return node
        name = node.id
        if name not in self.globalnames:
            return node
        self.lazycounts[name] += 1
        return ast.Call(ast.Name(self.lazyname, ast.Load()), [ast.Call(ast.Name('globals', ast.Load()), [], []), ast.Str(name)], [])
