
class SocketWrapper:
    SOCKET_BUFFER = 1024

    def __init__(self, socket):
        self.socket = socket

    def receive(self):
        return self.socket.recvfrom(self.SOCKET_BUFFER)