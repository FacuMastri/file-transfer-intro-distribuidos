import os, queue
from socket import AF_INET, SOCK_DGRAM, socket
from lib.packet import Packet
from lib.client_worker import ClientWorker

BUCKET_DIRECTORY = "src/server/files/"

SOCKET_BUFFER = 4096
SERVER_TIMEOUT = 10


class Server:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def start(self):
        if not os.path.exists("%s" % BUCKET_DIRECTORY):
            os.makedirs(BUCKET_DIRECTORY)
        server_socket = self._create_socket()
        self.logger.info(f"FTP server up in port {(self.host, self.port)}")
        # TODO cola de mensajes para manejar multiples clientes
        worker = True
        while True:
            data, client_address = server_socket.recvfrom(SOCKET_BUFFER)
            self.logger.info(f"Received message from {client_address}")
            packet = Packet.from_bytes(data)
            if packet.syn:
                #  TODO verificar que hay suficiente espacio en disco para el archivo - validar con el barba
                worker = ClientWorker(
                    queue.Queue(), client_address, packet.filename, self.logger
                )
                self.logger.info(f"created new worker with filename {packet.filename}")
                # TODO worker.iniciar_comunicacion
            else:
                # worker.put(packet)
                self.logger.info(f"gave packet to {client_address}")
                worker.receive_packet(packet)
            # vuelve al loop

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
