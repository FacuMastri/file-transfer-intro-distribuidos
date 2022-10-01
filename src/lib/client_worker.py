import os
import threading
from lib.packet import Packet
from socket import AF_INET, SOCK_DGRAM, socket
from lib.blocking_queue import BlockingQueue
from lib.stop_and_wait_manager import StopAndWaitManager
from upload import READ_BUFFER

BUCKET_DIRECTORY = "src/server/files/"


class ClientWorker(threading.Thread):
    TIMEOUT = 3
    READ_BUFFER = 1024

    def __init__(self, blocking_queue, client_address, file_name, logger, isDownload):
        self.packet_number = 0
        self.isDownload = isDownload
        self.address = client_address
        self.file = open(f"%s{file_name}" % BUCKET_DIRECTORY, "wb")
        self.logger = logger
        self.blocking_queue = blocking_queue
        output_socket = socket(AF_INET, SOCK_DGRAM)
        input_stream = BlockingQueue(blocking_queue)
        self.protocol = StopAndWaitManager(output_socket, input_stream, client_address, logger)
        threading.Thread.__init__(self)

    def run(self):
        if self.isDownload:
            self.send_packet()
        else:
            self.protocol.send_ack(0)
            self.receive_packet()

    def receive_packet(self):
        payload = 1
        while payload:
            try:
                payload = self.protocol.receive_data()
                self.logger.info(f"received payload from {self.address}")
                self.file.write(payload)

            except Exception as e:
                self.logger.info(e)
                self.file.close()
                os.remove(self.file.name) # TODO recibir ruta completa
                self.logger.info("exception ocurred, incomplete file removes")

        # TODO server_socket.settimeout(SERVER_TIMEOUT) agregar timeout de cliente
        # TODO refactorizar esto para que este adentro del protocolo.
        # hay que hacer una entidad que encapsule a la cola y al socket al mismo tiempo. asi cuando hago un recv/pop desde el cliente o el worker funciona de la misma manera
        # ese pop tiene que ser bloqueante y timeouteado. la cola provee esas funcionalidades.


    def send_packet(self):
        data = self.file.read(READ_BUFFER)
        # while data:
        self.protocol.send_data(data, self.file.name)
            # data = self.file.read(READ_BUFFER)

        # self.protocol.finish_upload_connection(self.file.name)
        # self.logger.info("Upload complete!")

    def put(self, packet):
        self.blocking_queue.put(packet)

    def _send_ack(self, server_socket, client_address):
        server_socket.sendto(Packet.ack_packet(0).to_bytes(), client_address)
        self.logger.debug("ACK sent, file correctly received")
