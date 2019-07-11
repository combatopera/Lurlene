# Copyright 2014, 2018, 2019 Andrzej Cichocki

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

from pathlib import Path
import unittest, subprocess

class TestExpected(unittest.TestCase):

    def test_expected(self):
        project = Path(__file__).parent.parent
        # FIXME: Instead of overriding channels, do not load personal config.
        command = [project / 'lc2txt.py', '--config', 'chipchannels = 3']
        expected = project / 'expected'
        for path in expected.glob('**/*'):
            if not path.is_dir():
                with path.open() as f:
                    for e, a in zip(f.read().splitlines(), subprocess.check_output(command + ["%s.py" % (project / path.relative_to(expected))]).decode().splitlines()):
                        self.assertEqual(e, a)
