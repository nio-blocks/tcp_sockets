from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..tcp_asynch_client_block import TCPAsynchClient


class TestTCPAsynchClient(NIOBlockTestCase):

    @patch('socket.socket')
    def test_connection(self, mock_socket):
        blk = TCPAsynchClient()
        self.configure_block(blk, {})
        blk.start()
        mock_socket.return_value.connect.assert_called_with(
            ('127.0.0.1', 50001))
        blk.stop()

    @patch('socket.socket')
    def test_process_signal(self, mock_socket):
        blk = TCPAsynchClient()
        self.configure_block(blk, {
            'message': '{{ $hello }}\n',
            'host': '1.2.3.4',
            'port': '1234'}),
        blk.start()
        blk.process_signals([Signal({'hello': 'n.io'})])
        mock_socket.return_value.connect.assert_called_with(('1.2.3.4', 1234))
        mock_socket.return_value.send.assert_called_with('n.io\n')
        blk.stop()

    @patch('socket.socket')
    def test_receive_message(self, mock_socket):
        mock_socket.return_value.recv.return_value = 'message'
        blk = TCPAsynchClient()
        self.configure_block(blk, {})
        blk.start()
        blk.stop()
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {
                'data': mock_socket.return_value.recv.return_value,
                'host': ('127.0.0.1', 50001),
            }
        )
