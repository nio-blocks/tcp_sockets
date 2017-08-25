import socket

from nio import GeneratorBlock
from nio.command import command
from nio.properties import StringProperty, IntProperty, VersionProperty
from nio.signal.base import Signal
from nio.util.threading.spawn import spawn


@command("current_connections", method='_list_connections')
class TCPStreamer(GeneratorBlock):

    host = StringProperty(title='IP Address', default='127.0.0.1')
    port = IntProperty(title='Port', default=50001)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self._main_thread = None
        self._kill = False
        self._connections = {}
        self._recv_threads = {}

    def start(self):
        super().start()
        self._main_thread = spawn(self._tcp_server)

    def stop(self):
        self._kill = True
        try:
            self._main_thread.join(1)
        except:
            self.logger.warning('main thread had already exited before join')
        self._connections = {}
        self._recv_threads = {}
        super().stop()

    def _recv(self, conn, addr, buffer_size):
        with conn:
            while not self._kill:
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
                    self._connections.pop(addr[0])
                    break

        self.logger.error('popped and closed the connection in _recv for host '
                          '{}'.format(addr[0]))

    def _tcp_server(self):
        self.logger.debug('started server thread')
        buffer_size = 1024
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host(), self.port()))
            s.listen(1)
            while not self._kill:
                self.logger.debug('listening for connections')
                conn, addr = s.accept()
                host = addr[0]

                # keep track of all accepted connections
                if host not in self._connections:
                    # new connection
                    self._connections[host] = conn
                else:
                    # the address has already been connected to, and it never
                    # closed itself (likely due to power loss).
                    # Tear down the old connection and make a new one on the
                    # same address

                    # closing the connection should cause the thread used by
                    # that connection to exit
                    self.logger.debug('Accepted a connection from an address '
                                      'already in use: {}, closing connection '
                                      'object: {}'
                                      .format(host, self._connections[host]))
                    self._connections[host].close()
                    try:
                        self._recv_threads[host].join()
                    except:
                        self.logger.debug('recv thread already exited before '
                                          'join')
                    self._connections[host] = conn

                self.logger.debug('{} connected'.format(addr))

                recv_thread = spawn(self._recv, conn, addr, buffer_size)
                self._recv_threads[host] = recv_thread

    def _list_connections(self):
        return self._connections
