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
        self._kill = False

    def start(self):
        super().start()
        spawn(self._tcp_server)

    # def process_signals(self, signals):
        # for signal in signals:
            # resp = self.response(signal).encode('utf-8')
            # try:
                # self.conn.sendto(resp, self.client(signal))
                # self.logger.debug('sent response {}'.format(resp))
            # except:
                # self.logger.exception('failed to send response')

    def stop(self):
        self._kill = True
        super().stop()

    def _recv(self, conn, addr, buffer_size):
        self.logger.debug('recv called')
        with conn:
            while self._kill == False:
                data = conn.recv(buffer_size)
                self.logger.debug('received data {}'.format(data))
                if data:
                    self.notify_signals([Signal(
                        {"data": data, "addr": addr})])
                if not data:
                    self.logger.debug(
                        'connection closed by remote client '
                        '{}'.format(addr))
                    break

    def _tcp_server(self):
        self.logger.debug('started server thread')
        buffer_size = 1024
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.IP_addr(), self.port()))
            s.listen(1)
            while self._kill == False:
                self.logger.debug('listening for connections')
                conn, addr = s.accept()
                self.logger.debug('{} connected'.format(addr))
                self._recv(conn, addr, buffer_size)
