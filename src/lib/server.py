import os
import queue
from socket import AF_INET, SOCK_DGRAM, socket

from lib.client_worker import ClientWorker
from lib.constants import BUFFER_RECV_SOCKET
from lib.packet import Packet


class Server:
    def __init__(self, host: str, port: int, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def start(self, protocol, storage_path):

        if not os.path.exists("%s" % storage_path):
            os.makedirs(storage_path)

        server_socket = self._create_socket()
        self.logger.info(f"FTP server up in {(self.host, self.port)}")

        workers = {}

        while True:
            data, client_address = server_socket.recvfrom(BUFFER_RECV_SOCKET)
            self.logger.debug(f"Received message from {client_address}")
            packet = Packet.from_bytes(data)
            if packet.is_syn():
                worker = ClientWorker(
                    queue.Queue(),
                    client_address,
                    packet.filename,
                    self.logger,
                    packet.is_upload,
                    protocol,
                    storage_path,
                )
                workers[client_address] = worker
                workers[client_address].start()
                self.logger.info(f"Created new worker with key {client_address} and filename {packet.filename}")
                for key in list(workers.keys()):
                    if not workers.get(key).is_alive():
                        self.logger.debug(f"deleted client thread {key}")
                        del workers[key]
            else:
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
