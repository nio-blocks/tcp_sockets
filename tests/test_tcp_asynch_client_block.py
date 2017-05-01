from unittest.mock import patch, MagicMock
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..tcp_asynch_client_block import TCPAsynchClient


class TestTCPAsynchClient(NIOBlockTestCase):

    def test_connection(self):
        with patch('socket.socket') as mock_socket:
            blk = TCPAsynchClient()
            self.configure_block(blk, {})
            blk.start()
            self.assertEqual(1, mock_socket.return_value.connect.call_count)
            mock_socket.return_value.connect.assert_called_with(
                ('127.0.0.1', 50001))
            blk.stop()

    def test_connection_retry(self):
        with patch('socket.socket') as mock_socket:
            blk = TCPAsynchClient()
            self.configure_block(blk, {})
            mock_socket.return_value.connect.side_effect = [
                Exception,
                MagicMock(),
            ]
            blk.start()
            from time import sleep
            sleep(1.1)
            self.assertEqual(2, mock_socket.return_value.connect.call_count)
            mock_socket.return_value.connect.assert_called_with(
                ('127.0.0.1', 50001))
            blk.stop()

    def test_process_signal(self):
        with patch('socket.socket') as mock_socket:
            blk = TCPAsynchClient()
            self.configure_block(blk, {
                'message': '{{ $hello }}\n',
                'host': '1.2.3.4',
                'port': '1234'}),
            blk.start()
            blk.process_signals([Signal({'hello': 'n.io'})])
            mock_socket.return_value.connect.assert_called_with(
                ('1.2.3.4', 1234))
            mock_socket.return_value.send.assert_called_with('n.io\n')
            blk.stop()

    def test_process_signal_reconnect(self):
        with patch('socket.socket') as mock_socket:
            blk = TCPAsynchClient()
            self.configure_block(blk, {
                'message': '{{ $hello }}\n',
                'host': '1.2.3.4',
                'port': '1234'}),
            mock_socket.return_value.connect.side_effect = Exception
            blk.start()
            blk.process_signals([Signal({'hello': 'n.io'})])
            mock_socket.return_value.connect.assert_called_with(
                ('1.2.3.4', 1234))
            mock_socket.return_value.send.assert_called_with('n.io\n')
            blk.stop()

    def test_receive_message(self):
        with patch('socket.socket') as mock_socket:
            blk = TCPAsynchClient()
            self.configure_block(blk, {})
            mock_socket.return_value.recv.return_value = b'message'
            blk.start()
            self.assertDictEqual(
                self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                {
                    'data': b'message',
                    'host': ('127.0.0.1', 50001),
                }
            )
            blk.stop()

    def test_reconnect_on_close(self):
        with patch('socket.socket') as mock_socket:
            blk = TCPAsynchClient()
            self.configure_block(blk, {'reconnect': True})
            mock_socket.return_value.recv.side_effect = [
                b'',
                b'message'
            ]
            blk.start()
            self.assertDictEqual(
                self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
                {
                    'data': b'',
                    'host': ('127.0.0.1', 50001),
                }
            )
            from time import sleep
            sleep(1.1)
            self.assertEqual(2, mock_socket.return_value.connect.call_count)
            self.assertDictEqual(
                self.last_notified[DEFAULT_TERMINAL][1].to_dict(),
                {
                    'data': b'message',
                    'host': ('127.0.0.1', 50001),
                }
            )
            blk.stop()
