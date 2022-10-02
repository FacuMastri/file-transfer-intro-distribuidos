import os
import queue
from socket import AF_INET, SOCK_DGRAM, socket

from lib.client_worker import ClientWorker
from lib.constants import BUFFER_RECV_SOCKET
from lib.packet import Packet

BUCKET_DIRECTORY = "src/server/files/"


class Server:
    def __init__(self, host: str, port: int, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def start(self, protocol):
        if not os.path.exists("%s" % BUCKET_DIRECTORY):
            os.makedirs(BUCKET_DIRECTORY)
        server_socket = self._create_socket()
        self.logger.info(f"FTP server up in port {(self.host, self.port)}")
        workers = {}
        while True:
            data, client_address = server_socket.recvfrom(BUFFER_RECV_SOCKET)
            self.logger.info(f"Received message from {client_address}")
            packet = Packet.from_bytes(data)
            if packet.is_syn():
                # TODO verificar que hay suficiente espacio en disco para el archivo - validar con el barba
                worker = ClientWorker(
                    queue.Queue(),
                    client_address,
                    packet.filename,
                    self.logger,
                    packet.is_upload,
                    protocol,
                )
                workers[client_address] = worker
                workers[client_address].start()
                self.logger.info(f"Created new worker with filename {packet.filename}")
            else:
                # TODO ver lo del get
                workers[client_address].put((data, client_address))

    def _create_socket(self):
        server_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            server_socket.bind((self.host, self.port))
        except Exception as e:
            self.logger.error("Port already in use")
            raise e
        return server_socket

    def stop(self):
        raise NotImplementedError()
