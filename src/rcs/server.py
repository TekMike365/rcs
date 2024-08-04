import errno
import socket
import threading

from .request_handler import RequestHandler


class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8080
    timeout_sec: float | None = 0.0
    reuse_addr: bool = True
    data_buf: int = 1024


class Server:
    def __init__(self, cfg: ServerConfig, request_handler: RequestHandler) -> None:
        self.cfg = cfg
        self.request_handler = request_handler
        self._soc: socket.socket | None = None
        self._thr: threading.Thread | None = None

    def get_socket(self) -> socket.socket | None:
        return self._soc

    def start(self) -> None:
        if isinstance(self._soc, socket.socket) and isinstance(
            self._thr, threading.Thread
        ):
            return
        if isinstance(self._soc, socket.socket) or isinstance(
            self._thr, threading.Thread
        ):
            raise Exception("Uh-oh! Something went wrong.")

        self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._soc.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, self.cfg.reuse_addr
        )
        self._soc.settimeout(self.cfg.timeout_sec)
        self._soc.bind((self.cfg.host, self.cfg.port))

        self._soc.listen(10)

        self._thr = threading.Thread(target=self._handle_connections)
        self._thr.start()

    def stop(self) -> None:
        if self._soc is None:
            return

        self._soc.close()
        self._soc = None

        self._thr = None

    def _handle_connections(self) -> None:
        while isinstance(self._soc, socket.socket):
            try:
                conn, addr = self._soc.accept()

                request = self._recieve_request(conn)
                response = self.request_handler.handle_request(request)
                msg_len = len(response)
                while msg_len > 0:
                    sent = conn.send(bytes(response, "ascii"))
                    if sent == 0:
                        raise RuntimeError("socket connection broken.")

                    msg_len -= sent
                    response = response[sent:]

                conn.close()
            except OSError as e:
                en = e.args[0]
                if en == errno.EAGAIN or e == errno.EWOULDBLOCK:
                    continue
                break

    def _recieve_request(self, soc: socket.socket) -> str:
        request = ""

        while True:
            data = soc.recv(self.cfg.data_buf)
            if not data:
                break

            request += data.decode("ascii")

            if len(data) <= self.cfg.data_buf:
                break

        return request
