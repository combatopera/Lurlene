# Copyright 2014, 2018 Andrzej Cichocki

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

from .bg import SimpleBackground
from .const import appconfigdir
from .iface import Config, YMFile
from aridity import Context, Repl
from aridimpl.util import NoSuchPathException
from aridimpl.model import Function, Number, Text
import sys, logging, os, numbers, importlib

log = logging.getLogger(__name__)

class ConfigName:

    envparam = 'PYM2149_CONFIG'
    workspacepath = os.path.join(appconfigdir, 'workspace')
    configfilename = 'chip.py'
    defaultslabel = 'defaults'

    @classmethod
    def pathofname(cls, name):
        return os.path.join(cls.workspacepath, name, cls.configfilename)

    @classmethod
    def getnameornone(cls):
        try:
            name = os.environ[cls.envparam]
            return name if name else None # Empty means defaults.
        except KeyError:
            if os.path.exists(cls.workspacepath):
                confignames = sorted(name for name in os.listdir(cls.workspacepath) if os.path.exists(cls.pathofname(name)))
                for i, name in enumerate([cls.defaultslabel] + confignames):
                    print("%s) %s" % (i, name), file=sys.stderr)
                sys.stderr.write('#? ')
                number = int(input())
                if number < 0:
                    raise Exception(number)
                if number:
                    return confignames[number - 1]

    def __init__(self, *params, **kwargs):
        try:
            args = kwargs['args']
        except KeyError:
            args = sys.argv[1:]
        if len(args) != len(params):
            raise Exception("Expected %s but got: %s" % (params, args))
        try:
            nameornone = kwargs['nameornone']
        except KeyError:
            nameornone = self.getnameornone()
        self.pathornone = None if nameornone is None else self.pathofname(nameornone)
        self.additems = list(zip(params, args))

    def isdefaults(self):
        return self.pathornone is None

    def path(self):
        if self.pathornone is None:
            raise Exception("Using %s." % self.defaultslabel)
        return self.pathornone

    def applyitems(self, config):
        for name, value in self.additems:
            setattr(config, name, value)

def wrap(value):
    return (Number if isinstance(value, numbers.Number) else Text)(value)

class AsContext:

    def __init__(self, parent, obj):
        self.parent = parent
        self.obj = obj

    def resolved(self, name):
        try:
            return wrap(getattr(self.obj, name))
        except AttributeError:
            return self.parent.resolved(name)

class PathInfo:

    def __init__(self, configname):
        self.configname = configname

    def mark(self):
        path = self.configname.path()
        self.mtime = os.stat(path).st_mtime
        return path

    def load(self, di = None):
        evalcontext = {}
        def imp(module, name):
            evalcontext[name] = getattr(importlib.import_module(module, __package__), name)
        imp('.ym2149', 'stclock')
        imp('.program', 'DefaultNote')
        imp('.const', 'midichannelcount')
        imp('.iface', 'YMFile')
        if di is not None:
            evalcontext['di'] = di
        context = Context()
        def py(context, *clauses):
            return wrap(eval(' '.join(c.cat() for c in clauses), evalcontext))
        context['py',] = Function(py)
        def ymfile(context, resolvable):
            try:
                ymfile = di(YMFile)
            except Exception:
                raise NoSuchPathException
            return resolvable.resolve(AsContext(context, ymfile))
        context['ymfile',] = Function(ymfile)
        with Repl(context) as repl:
            repl.printf(". $/(%s %s)", os.path.dirname(__file__), 'defaultconf.arid')
            if not self.configname.isdefaults():
                context.loadpath(self.mark())
        config = ConfigImpl(context)
        self.configname.applyitems(config)
        evalcontext['config'] = config
        return config

    def reloadornone(self):
        path = self.configname.path()
        if os.stat(path).st_mtime != self.mtime:
            log.info("Reloading: %s", path)
            return self.load()

class ConfigSubscription(SimpleBackground):

    def __init__(self, configname, consumer):
        self.configname = configname
        self.consumer = consumer

    def start(self):
        self.pathinfo = PathInfo(self.configname)
        self.consumer(self.pathinfo.load())
        SimpleBackground.start(self, self.bg, self.Sleeper())

    def bg(self, sleeper):
        if not self.configname.isdefaults():
            while True:
                sleeper.sleep(1)
                if self.quit:
                    break
                config = self.pathinfo.reloadornone()
                if config is not None:
                    self.consumer(config)

class ConfigImpl(Config):

    def __init__(self, context):
        self.pRiVaTe = context

    def __getattr__(self, name):
        try:
            return self.pRiVaTe.resolved(name).unravel()
        except NoSuchPathException:
            raise AttributeError(name)
