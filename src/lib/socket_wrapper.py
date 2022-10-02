from lib.constants import BUFFER_RECV_SOCKET


class SocketWrapper:
    def __init__(self, socket):
        self.socket = socket

    def receive(self):
        return self.socket.recvfrom(BUFFER_RECV_SOCKET)
