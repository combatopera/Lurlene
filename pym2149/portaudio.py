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

from .iface import AmpScale, Platform, Stream, Config
from .jackclient import BufferFiller
from .nod import Node
from .out import FloatStream, StereoInfo
from .shapes import floatdtype
from diapyr import types
from pyaudio import PyAudio, paFloat32, paContinue
import numpy as np, logging, threading

log = logging.getLogger(__name__)

class Ring: # There is a very similar ring impl in outjack, not sure if possible to unduplicate.

    def __init__(self, ringsize, bufsize, coupling):
        # The last one should be zeros for quiet initial underrun:
        self.outbufs = [np.zeros(bufsize, dtype = floatdtype) for _ in range(ringsize)]
        self.unconsumed = [False] * ringsize
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.readcursor = self.writecursor = 0
        self.size = ringsize
        self.coupling = coupling

    def flip(self):
        with self.lock:
            self.unconsumed[self.writecursor] = True
            self.writecursor = (self.writecursor + 1) % self.size
            if self.unconsumed[self.writecursor]:
                if not self.coupling:
                    log.error('Overrun!') # Log exactly once per overrun.
                while self.unconsumed[self.writecursor]: # Use while in case of spurious wakeup.
                    self.cv.wait()
            # FIXME: PortAudio may still be reading from this outbuf.
            return self.outbufs[self.writecursor]

    def consume(self):
        with self.lock:
            if self.unconsumed[self.readcursor]:
                self.unconsumed[self.readcursor] = False
                self.readcursor = (self.readcursor + 1) % self.size
                self.cv.notify()
            else:
                log.warning('Underrun!') # Return same outbuf again,
            return self.outbufs[(self.readcursor - 1) % self.size]

class PortAudioClient(Platform):

    @types(Config, StereoInfo)
    def __init__(self, config, stereoinfo):
        config = config.PortAudio
        self.outputrate = config['outputrate'] # TODO: Find best rate supported by system.
        self.buffersize = config['buffersize']
        self.chancount = stereoinfo.getoutchans.size
        self.ring = Ring(config['ringsize'], self.chancount * self.buffersize, config['coupling'])

    def start(self):
        self.p = PyAudio()
        self.stream = self.p.open(
                rate = self.outputrate,
                channels = self.chancount,
                format = paFloat32,
                output = True,
                frames_per_buffer = self.buffersize,
                stream_callback = self._callback)

    def initial(self):
        return self.ring.outbufs[0]

    def flip(self):
        return self.ring.flip()

    def _callback(self, in_data, frame_count, time_info, status_flags):
        return self.ring.consume(), paContinue

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class PortAudioStream(Node, Stream, metaclass = AmpScale):

    log2maxpeaktopeak = 1

    @types(StereoInfo, FloatStream, PortAudioClient)
    def __init__(self, stereoinfo, wavs, client):
        super().__init__()
        self.chancount = stereoinfo.getoutchans.size
        self.wavs = wavs
        self.client = client

    def start(self):
        self.filler = BufferFiller(self.chancount, self.client.buffersize, self.client.initial, self.client.flip, True)

    def callimpl(self):
        self.filler([self.chain(wav) for wav in self.wavs])

    def flush(self):
        pass

    def stop(self):
        pass