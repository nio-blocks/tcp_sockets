import socket

from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from unittest.mock import patch, MagicMock

from nio.testing.modules.scheduler.scheduler import JumpAheadScheduler

from ..tcp_streamer_block import TCPStreamer
from time import sleep


class TestTCPStreamer(NIOBlockTestCase):

    def test_default_configurations(self):
        blk = TCPStreamer()
        self.configure_block(blk, {})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value = 'datum'
            mock_socket.return_value.__enter__.return_value.\
                accept.return_value = (mock_connect, ('127.0.0.1', 50001))
            blk.start()
            # waiting for signal to be notified
            from time import sleep; sleep(0.1)
            blk.stop()
            mock_socket.return_value.__enter__.return_value.\
                bind.assert_called_once_with(('127.0.0.1', 50001))
            mock_socket.return_value.__enter__.return_value.\
                listen.assert_called_once_with(1)

        self.assertTrue(len(self.last_notified[DEFAULT_TERMINAL]) > 0)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(), {
                'addr': ('127.0.0.1', 50001),
                'data': 'datum'
            })

    def test_other_configurations(self):
        blk = TCPStreamer()
        self.configure_block(blk, {'host': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.__enter__.return_value.\
                accept.return_value = (MagicMock(), MagicMock())
            blk.start()
            blk.stop()
            mock_socket.return_value.__enter__.return_value.\
                bind.assert_called_once_with(('1.2.3.4', 12345))

    def test_no_data(self):
        blk = TCPStreamer()
        self.configure_block(blk, {'host': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value = None
            mock_socket.return_value.__enter__.return_value.\
                accept.return_value = (mock_connect, ('1.2.3.4', 12345))

            blk.start()

            mock_socket.return_value.__enter__.return_value.\
                bind.assert_called_once_with(('1.2.3.4', 12345))
            mock_socket.return_value.__enter__.return_value.\
                listen.assert_called_once_with(1)

            sleep(1)
            self.assert_num_signals_notified(0)
            # the connection won't be out of blk._connections due to accept
            # always returning an identical connection, but close and
            # shutdown will have been called
            mock_connect.close.assert_called_once_with()

            blk.stop()

    def test_data_then_reconnect(self):
        """
        Initially receive data from one client, then have that same client
        (same host,port configuration) reconnect without ever having called
        it's close() method. The reconnect should result in the old connection
        being closed and a new connection being created with the same host and
        port as the destructed one.
        """

        blk = TCPStreamer()
        self.configure_block(blk, {'host': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value = 'datum'
            mock_socket.return_value.__enter__.return_value. \
                accept.return_value = (mock_connect, ('1.2.3.4', 12345))

            blk.start()

            sleep(1)
            self.assert_num_signals_notified(0)

            blk.stop()
