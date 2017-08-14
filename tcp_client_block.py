import socket

from nio.block.base import Block
from nio.properties import StringProperty, BoolProperty, IntProperty, \
    VersionProperty


class TCPClient(Block):

    host = StringProperty(title='IP Address', default='127.0.0.1')
    message = StringProperty(title='Message', default='GET / HTTP/1.1\n')
    port = IntProperty(title='Port', default=50001)
    expect_response = BoolProperty(title='Expect response?', default=True)
    version = VersionProperty('0.0.1')

    def process_signals(self, signals):
        for signal in signals:
            message = self.message(signal).encode('utf-8')
            response = self.send_message(message)
            if response:
                signal.response = response
        self.notify_signals(signals)

    def send_message(self, message):
        response = None
        buffer_size = 8192
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host(), self.port()))
        s.send(message)
        if self.expect_response():
            response = s.recv(buffer_size)
        s.shutdown(2)
        s.close()
        return response
