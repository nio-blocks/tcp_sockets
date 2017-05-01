import socket

from nio.block.base import Block
from nio.signal.base import Signal
from nio.properties import StringProperty, IntProperty, BoolProperty, \
                           VersionProperty, Property
from nio.util.threading.spawn import spawn
from nio.block.mixins import Retry


class TCPAsynchClient(Retry, Block):

    host = StringProperty(title='IP Address', default='127.0.0.1')
    message = Property(title='Message', default='GET / HTTP/1.1\n')
    port = IntProperty(title='Port', default=50001)
    reconnect = BoolProperty(title='Reconnect when host closes connection',
                             default=False)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._receive_thread = None
        self._connect_thread = None
        self._kill = False
        self._conn = None
        self._buffer_size = 8192
        self._host = None

    def start(self):
        super().start()
        self._connect_thread = spawn(self.execute_with_retry, self._connect)
        self._receive_thread = spawn(self._receive)

    def stop(self):
        self._kill = True
        try:
            self._receive_thread.join(1)
        except:
            self.logger.warning(
                'receive thread had already exited before join')
        try:
            self._connect_thread.join(1)
        except:
            self.logger.warning(
                'connect thread had already exited before join')
        if self._conn:
            self._cleanup()
        super().stop()

    def process_signals(self, signals):
        for signal in signals:
            message = self.message(signal)
            if self._conn:
                self._send(message)
            else:
                self.logger.error('Inactive connection, dropping signal')
                self._connect_thread = spawn(self.execute_with_retry,
                                             self._connect)

    def _connect(self):
        self.logger.debug('Connecting ...')
        self._conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = (self.host(), self.port())
        self._conn.connect(self._host)
        self.logger.debug('Connected to {}'.format((self.host(), self.port())))

    def _send(self, message):
        if not self._kill:
            self._conn.send(message)
            self.logger.debug('Sent {}'.format(message))

    def _receive(self):
        while not self._kill:
            if self._conn:
                data = self._conn.recv(self._buffer_size)
                self.logger.debug('Received {}'.format(data))
                self.notify_signals(Signal({'data': data, 'host': self._host}))
                if not data:
                    self.logger.debug('Remote host closed connection')
                    self._conn = None
                    if not self.reconnect():
                        break
                    else:
                        self._connect_thread = spawn(self.execute_with_retry,
                                                     self._connect)

    def _cleanup(self):
        self._conn.shutdown(2)
        self._conn.close()
        self.logger.debug('Closed connection')