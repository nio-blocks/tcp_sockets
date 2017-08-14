from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from unittest.mock import patch, MagicMock

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
            sleep(0.1)
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
                accept.side_effect = [(mock_connect, ('1.2.3.4', 12345)),
                                      Exception]

            blk.start()

            mock_socket.return_value.__enter__.return_value.\
                bind.assert_called_once_with(('1.2.3.4', 12345))
            mock_socket.return_value.__enter__.return_value.\
                listen.assert_called_once_with(1)

            sleep(0.1)
            self.assertEqual(len(blk._connections), 0)

            blk.stop()

            # since no data is received, no signals should have been notified.
            self.assert_num_signals_notified(0)

    def test_reconnect(self):
        blk = TCPStreamer()
        self.configure_block(blk, {'host': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value = 'datum'
            mock_socket.return_value.__enter__.return_value. \
                accept.side_effect = [(mock_connect, ('1.2.3.4', 12345)),
                                      (mock_connect, ('1.2.3.4', 12345))]

            blk.start()
            sleep(0.1)

            # this should always be one, as reconnect pops the old connection
            # and adds the new one on the same host
            self.assertEqual(len(blk._connections), 1)
            self.assertEqual(len(blk._recv_threads), 1)

            blk.stop()

            # since this block receives data, it won't close the connection
            # itself. If close is called, it's because a new connection on the
            # same host has connected.
            self.assertGreater(mock_connect.close.call_count, 0)

    def test_multihost(self):
        blk = TCPStreamer()
        self.configure_block(blk, {'host': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value = 'datum'
            mock_socket.return_value.__enter__.return_value. \
                accept.side_effect = [(mock_connect, ('1.2.3.4', 12345)),
                                      (mock_connect, ('2.3.4.5', 12000)),
                                      (mock_connect, ('2.3.4.5', 12000))]

            blk.start()
            sleep(0.1)

            self.assertEqual(len(blk._connections), 2)
            self.assertEqual(len(blk._recv_threads), 2)

            blk.stop()

            self.assertEqual(len(blk._connections), 0)
            self.assertEqual(len(blk._recv_threads), 0)

            self.assertGreater(mock_connect.close.call_count, 0)
