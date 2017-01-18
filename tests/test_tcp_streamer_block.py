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
            # the connection won't be out of blk._connections due to accept
            # always returning an identical connection, but close will have
            # been called
            mock_connect.close.assert_called_once_with()

            blk.stop()

            self.assert_num_signals_notified(0)

    def test_reconnect(self):
        """Once the block is started, it will start creating a bunch of
        connections very quickly since accept is mocked to always return,
        and putting them in blk._connections. Since all of these
        connections are the same mocked connection object, close() will
        be called on the previous connection and be removed from the
        dict, replaced by the same connection object. So there should
        only ever be one connection in the dict at a time if reconnect
        functionality is working.
        """

        blk = TCPStreamer()
        self.configure_block(blk, {'host': '1.2.3.4', 'port': 12345})
        with patch('socket.socket') as mock_socket:
            mock_connect = MagicMock()
            mock_connect.recv.return_value = None
            mock_socket.return_value.__enter__.return_value. \
                accept.return_value = (mock_connect, ('1.2.3.4', 12345))

            blk.start()
            sleep(1.5)
            self.assertGreater(mock_connect.close.call_count, 0)
            blk.stop()

            # since no data is received, no signals should have been notified.
            self.assert_num_signals_notified(0)
            try:
                self.assertEqual(len(blk._connections), 1)
            except:
                # we caught the block in the middle of removing a connection
                # due to receiving no data. By this point, it is very
                # likely that another connection has come in and has called
                # close on the connection object, and this would be the case
                # if reconnect is working
                self.assertGreater(mock_connect.close.call_count, 0)
