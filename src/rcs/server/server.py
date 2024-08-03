import socket
import threading

from .config import ServerConfig


class Server:
    def __init__(self, cfg: ServerConfig) -> None:
        self.cfg = cfg
        self._soc: socket.socket | None = None
        self._thr: threading.Thread | None = None

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
        self._soc.bind((self.cfg.host, self.cfg.port))
        self._soc.listen(10)

        self._thr = threading.Thread(target=self._handle_connections)
        self._thr.start()

    def stop(self) -> None:
        if self._soc is None:
            return

        self._soc.close()
        self._soc = None

        if self._thr is threading.Thread and self._thr.is_alive():
            self._thr.join()
        self._thr = None

    def _handle_connections(self):
        while isinstance(self._soc, socket.socket):
            conn, addr = self._soc.accept()
            print(f"connected @ {addr}")
