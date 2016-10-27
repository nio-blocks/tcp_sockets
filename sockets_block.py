from nio.block.base import Block
from nio.signal.base import Signal
from nio.util.discovery import discoverable
from nio.properties import StringProperty, BoolProperty, IntProperty
from nio.properties import VersionProperty

import socket


@discoverable
class Sockets(Block):

    IP_addr = StringProperty(title='IP Address', default='127.0.0.1')
    message = StringProperty(title='Message', default='GET / HTTP/1.1')
    add_newline = BoolProperty(title='Add newline?', default=True)
    port = IntProperty(title='Port', default=80)
    version = VersionProperty('0.0.1')

    def process_signals(self, signals):
        """Overrideable method to be called when signals are delivered.
        This method will be called by the block router whenever signals
        are sent to the block. The method should not return the modified
        signals, but rather call `notify_signals` so that the router
        can route them properly.
        Args:
            signals (list): A list of signals to be processed by the block
            input_id: The identifier of the input terminal the signals are
                being delivered to
        """
        for signal in signals:
            pass
        self.TCP_client()

    def TCP_client(self):
        buffer_size = 8192
        msg = self.message().encode('utf-8')
        if self.add_newline:
            msg += bytes([10])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.IP_addr(),self.port()))
        s.send(msg)
        response = s.recv(buffer_size)
        s.shutdown(2)
        s.close()
        try:
            self.notify_signals([Signal({"response":response})])
        except:
            self.logger.exception(
                'Response is not valid: {}'.format(response))


