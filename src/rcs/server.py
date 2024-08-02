import socket
import threading


class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
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
        self._soc.bind((self.host, self.port))
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
        pass
