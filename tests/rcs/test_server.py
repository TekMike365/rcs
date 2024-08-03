import socket
import unittest

from src.rcs.server import Server, ServerConfig


class TestServer(unittest.TestCase):
    HOST = "127.0.0.1"
    PORT = 8080

    def setUp(self) -> None:
        server_cfg = ServerConfig()
        server_cfg.host = self.HOST
        server_cfg.port = self.PORT
        self.server = Server(server_cfg)

    def check_connection(self) -> bool:
        """
        Check if a socket is opened at HOST:PORT

        Returns:
            - true if a connection can be made
            - false if a connection cannot be made
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((self.HOST, self.PORT))
        except ConnectionRefusedError:
            return False
        return True

    def test_socket(self):
        """Test if a socket is created at a correct address"""
        self.server.start()
        self.assertEqual(self.check_connection(), True)
        self.server.stop()

    def test_socket_closed(self):
        """Test if a socket is properly closed"""
        self.server.start()
        self.assertEqual(self.check_connection(), True)
        self.server.stop()
        self.assertEqual(self.check_connection(), False)

    def test_stop_on_stopped(self):
        """Stopping already stopped server should do nothing."""
        self.server.stop()

    def test_start_on_running(self):
        """Starting already running server should do nothing."""
        self.server.start()
        self.assertEqual(self.check_connection(), True)
        self.server.start()
        self.assertEqual(self.check_connection(), True)
        self.server.stop()

    def test_restart(self):
        """Test proper restarting."""
        self.server.start()
        self.assertEqual(self.check_connection(), True)
        self.server.stop()

        self.server.start()
        self.assertEqual(self.check_connection(), True)
        self.server.stop()
