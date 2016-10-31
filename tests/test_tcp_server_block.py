from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from unittest.mock import patch, MagicMock
from threading import Event
from ..tcp_server_block import TCPserver


class TestTCPserver(NIOBlockTestCase):

    def test_default_configurations(self):
        blk = TCPserver()
        self.configure_block(blk, {})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value.decode.return_value = 'datum'
            mock_socket.return_value.accept.return_value = (
                mock_connect, ('127.0.0.1', 50001))
            blk.start()
            self.assertEqual(
                mock_socket.return_value.bind.call_count, 1)
            self.assertEqual(
                mock_socket.return_value.bind.call_args[0][0], 
                ('127.0.0.1', 50001))
            self.assertEqual(
                mock_socket.return_value.listen.call_count, 1)
            self.assertEqual(
                mock_socket.return_value.listen.call_args[0][0], 1)

        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]) > 0)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {
            'addr': ('127.0.0.1', 50001),
            'data': 'datum'
            })

    def test_other_configurations(self):
        blk = TCPserver()
        self.configure_block(blk, {'IP_addr': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            blk.start()
            mock_socket.return_value.bind.assert_called_once_with(
                ('1.2.3.4', 12345))
