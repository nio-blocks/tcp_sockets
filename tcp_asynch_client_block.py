import socket

from nio.block.base import Block
from nio.signal.base import Signal
from nio.properties import StringProperty, BoolProperty, IntProperty, \
                           VersionProperty, Property
from nio.util.threading.spawn import spawn


class TCPAsynchClient(Block):

    host = StringProperty(title='IP Address', default='127.0.0.1')
    message = Property(title='Message', default='GET / HTTP/1.1\n')
    port = IntProperty(title='Port', default=50001)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._main_thread = None
        self._kill = False
        self._conn = None
        self._buffer_size = 8192
        self._host = None

    def start(self):
        self._main_thread = spawn(self._connect)

    def stop(self):
        self._kill = True
        try:
            self._main_thread.join(1)
        except:
            self.logger.warning('main thread had already exited before join')
        self._conn.shutdown(2)
        self._conn.close()
        super().stop()

    def process_signals(self, signals):
        for signal in signals:
            message = self.message(signal)
            self.logger.debug('sending {}'.format(message))
            try:
                self._conn.send(message)
            except:
                # reopen connection
                self._main_thread.join(1)
                self._main_thread = spawn(self._connect)
                self._conn.send(message)

    def _connect(self):
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = (self.host(), self.port())
        self._conn.connect(self._host)
        self.logger.debug('Connected to {}'.format((self.host(), self.port())))
        self._receive()
        

    def _receive(self):
        # if remote host closes connection this loop runs out of control
        while not self._kill:
            data = self._conn.recv(self._buffer_size)
            if not data:
                break
            self.notify_signals(Signal({'data': data, 'host': self._host}))