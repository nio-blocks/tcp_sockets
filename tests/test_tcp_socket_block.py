from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..tcp_socket_block import TCPSocket
from unittest.mock import MagicMock, patch
import socket


class TestExample(NIOBlockTestCase):


    @patch('socket.socket')
    def test_default_configurations(self, mock_socket):
        """Default values trigger correct behavior"""

        mock_socket.return_value.recv.return_value = "Return Successful"
        blk = TCPSocket()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({"hello": "n.io"})])
        mock_socket.return_value.connect.assert_called_with(('127.0.0.1',50001))
        mock_socket.return_value.send.assert_called_with(b"GET / HTTP/1.1\n")
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {"response": mock_socket.return_value.recv.return_value})

    @patch('socket.socket')
    def test_process_signal(self, mock_socket):
        """Sends input signal to TCP server"""

        mock_socket.return_value.recv.return_value = "Return Successful"
        blk = TCPSocket()
        self.configure_block(blk, {'message': '{{$hello}}', 'IP_addr': '1.2.3.4', 'port': '12345'})
        blk.start()
        blk.process_signals([Signal({"hello": "n.io"})])
        mock_socket.return_value.connect.assert_called_with(('1.2.3.4',12345))
        mock_socket.return_value.send.assert_called_with(b"n.io\n")
        blk.stop()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {"response": mock_socket.return_value.recv.return_value})