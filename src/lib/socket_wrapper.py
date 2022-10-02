class SocketWrapper:
    SOCKET_BUFFER = 4096

    def __init__(self, socket):
        self.socket = socket

    def receive(self):
        return self.socket.recvfrom(self.SOCKET_BUFFER)

    def settimeout(self, timeout):
        self.socket.settimeout(timeout)
