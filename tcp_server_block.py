from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.discovery import discoverable
from nio.properties import StringProperty, BoolProperty, IntProperty
from nio.properties import VersionProperty
from nio.util.threading.spawn import spawn
from threading import Event

import socket


@discoverable
class TCPserver(Block):

    IP_addr = StringProperty(title='IP Address', default='127.0.0.1')
    # message = StringProperty(title='Message', default='GET / HTTP/1.1')
    # add_newline = BoolProperty(title='Add newline?', default=True)
    response = StringProperty(title='Response', default='{{ $response }}')
    addr_field = StringProperty(title='Client IP Field', default='{{ $client_addr }}')
    port_field = StringProperty(title='Client Port Field', default='{{ $client_port }}')
    port = IntProperty(title='Port', default=80)
    version = VersionProperty('0.0.1')

    def __init__(self):
        super().__init__()
        self.conn = None
        self.s = None
        self._kill = False
    
    def start(self):
        spawn(self._tcp_server)
    
    def process_signals(self, signals):
        for signal in signals:
            resp = self.response(signal).encode('utf-8')
            self.conn.sendto(resp, (self.addr_field(signal),int(self.port_field(signal))))

    def stop(self):
        self._kill = True
        if self.conn:
            self.conn.close()
        self.s.close()
        self.logger.debug('closed connection, socket')
            
    def _tcp_server(self):
        self.logger.debug('started server thread')
        buffer_size = 8192
        self.s = socket.socket()
        self.s.bind((self.IP_addr(),self.port()))
        while self._kill == False:
            self.s.listen(1)
            self.logger.debug('listening for connections')
            self.conn, addr = self.s.accept()
            self.logger.debug(str(addr) + ' connected')
            data = self.conn.recv(1024).decode()
            try:
                self.notify_signals(
                    [Signal(
                        {"data":data,
                        "client_addr":addr[0],
                        "client_port":addr[1]})])

            except:
                self.logger.exception(
                    'Notify signals failed, received: {}'.format(data))


