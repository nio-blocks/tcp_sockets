from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.discovery import discoverable
from nio.properties import StringProperty, BoolProperty, IntProperty, Property
from nio.properties import VersionProperty
from nio.util.threading.spawn import spawn
from threading import Event
import socket


@discoverable
class TCPserver(Block):

    IP_addr = StringProperty(title='IP Address', default='127.0.0.1')
    response = StringProperty(title='Response', default='{{ $response }}')
    client = Property(title='Client IP/Port', default='{{ $addr }}')
    port = IntProperty(title='Port', default=50001)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self.conn = None
        self.s = None
        self._kill = False

    def start(self):
        super().start()
        spawn(self._tcp_server)

    def process_signals(self, signals):
        for signal in signals:
            resp = self.response(signal).encode('utf-8')
            try:
                self.conn.sendto(resp, self.client(signal))
                self.logger.debug('sent response {}'.format(resp))
            except:
                self.logger.exception('failed to send response')

    def stop(self):
        self._kill = True
        if self.conn:
            self.conn.close()
            self.logger.debug('closed connection')
        self.s.close()
        self.logger.debug('closed socket')
        super().stop()

    def _tcp_server(self):
        self.logger.debug('started server thread')
        buffer_size = 8192
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.IP_addr(), self.port()))
        self.s.listen(1)
        self.logger.debug('listening for connections')
        self.conn, addr = self.s.accept()
        self.logger.debug('{} connected'.format(addr))
        while self._kill == False:
            data = self.conn.recv(buffer_size).decode()
            if data:
                self.notify_signals([Signal({"data": data, "addr": addr})])
            if not data:
                self.logger.debug('no data, breaking')
                self.conn.close()
                self.logger.debug('closed connection')
                self.s.close()
                self.logger.debug('closed socket')
                break
        _tcp_server()