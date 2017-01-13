import socket

from nio.block.base import Block
from nio.properties import StringProperty, IntProperty, VersionProperty
from nio.signal.base import Signal
from nio.util.threading.spawn import spawn


class TCPStreamer(Block):

    host = StringProperty(title='IP Address', default='127.0.0.1')
    port = IntProperty(title='Port', default=50001)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._thread = None
        self._kill = False
        self._conn_dict = {}

    def start(self):
        super().start()
        self._thread = spawn(self._tcp_server)

    def stop(self):
        self._kill = True
        self._thread.join(1)
        super().stop()

    def _recv(self, conn, addr, buffer_size):
        with conn:
            while self._kill == False:
                self.logger.debug('waiting for data from addr {}'.format(addr))
                data = conn.recv(buffer_size)
                self.logger.debug('received data {}'.format(data))
                if data:
                    self.notify_signals([Signal(
                        {"data": data, "addr": addr})])
                if not data:
                    self.logger.debug(
                        'connection closed by remote client '
                        '{}'.format(addr))
                    self._conn_dict.pop(addr)
                    break

    def _tcp_server(self):
        self.logger.debug('started server thread')
        buffer_size = 1024
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host(), self.port()))
            s.listen(1)
            while self._kill == False:
                self.logger.debug('listening for connections')
                conn, addr = s.accept()

                # keep track of all accepted connections
                if addr not in self._conn_dict:
                    # new connection
                    self._conn_dict.update({addr: conn})
                else:
                    # the address has already been connected to, and it never
                    # closed itself (likely due to power loss).
                    # Tear down the old connection and make a new one on the
                    # same address

                    # closing the connection should cause the thread used by
                    # that connection to exit
                    self._conn_dict[addr].close()
                    self._conn_dict[addr] = conn

                self.logger.debug('{} connected'.format(addr))

                spawn(self._recv, conn, addr, buffer_size)
