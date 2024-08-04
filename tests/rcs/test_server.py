import socket
import unittest

from src.rcs.server import Server, ServerConfig
from src.rcs.request_handler import RequestHandler


class EchoRH(RequestHandler):
    def handle_request(self, request: str) -> str:
        return request


class TestServer(unittest.TestCase):
    HOST = "127.0.0.1"
    PORT = 8080

    def __init__(self, methodName: str = "runTest") -> None:
        self.server = Server(ServerConfig(), RequestHandler())
        super().__init__(methodName)

    def setUp(self) -> None:
        server_cfg = ServerConfig()
        server_cfg.host = self.HOST
        server_cfg.port = self.PORT
        self.server = Server(server_cfg, EchoRH())

    def tearDown(self) -> None:
        self.server.stop()

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

    def send_msg(self, msg: str) -> str:
        """
        Sends message to server.

        Params:
            msg (str): message to be send

        Returns:
            str: response string
        """

        response = ""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
            soc.connect((self.HOST, self.PORT))
            soc.sendall(bytes(msg, "ascii"))
            response = soc.recv(len(msg))

        return response.decode("ascii")

    def test_setUp(self):
        """A test for my unittests setUp function."""
        self.server.start()

    def test_rec_send(self):
        """Test if a message is properly recieved and send."""

        self.server.start()

        msg = "Hello! This is a very sophysticated test."
        self.assertEqual(self.send_msg(msg), msg)

        self.server.stop()

    def test_rec_buff_size(self):
        """Test if a message of servers data_buf length is properly recieved."""

        self.server.start()

        msg = "L" * self.server.cfg.data_buf
        self.assertEqual(self.send_msg(msg), msg)

        self.server.stop()

    def test_rec_buff_plus_size(self):
        """Test if a message of higher than servers data_buf length is properly recieved."""

        self.server.start()

        msg = "L" * (self.server.cfg.data_buf + 50)
        self.assertEqual(self.send_msg(msg), msg[:-50])

        self.server.stop()

    def test_socket(self):
        """Test if a socket is created at a correct address"""

        self.server.start()
        self.assertTrue(self.check_connection())
        self.server.stop()

    def test_socket_closed(self):
        """Test if a socket is properly closed"""

        self.server.start()
        self.assertTrue(self.check_connection())
        self.server.stop()
        self.assertFalse(self.check_connection())

    def test_stop_on_stopped(self):
        """Stopping already stopped server should do nothing."""

        self.server.stop()

    def test_start_on_running(self):
        """Starting already running server should do nothing."""

        self.server.start()
        self.assertTrue(self.check_connection())
        self.server.start()
        self.assertTrue(self.check_connection())
        self.server.stop()

    def test_restart(self):
        """Test proper restarting."""

        self.server.start()
        self.assertTrue(self.check_connection())
        self.server.stop()

        self.server.start()
        self.assertTrue(self.check_connection())
        self.server.stop()
