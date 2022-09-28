import os
from lib.packet import Packet
from socket import AF_INET, SOCK_DGRAM, socket

BUCKET_DIRECTORY = "src/server/files/"


class ClientWorker:
    TIMEOUT = 3

    def __init__(self, blocking_queue, client_address, file_name, logger):
        self.packet_number = 0
        self.input_queue = blocking_queue
        self.client_address = client_address
        self.file = open(f"%s{file_name}" % BUCKET_DIRECTORY, "wb")
        self.logger = logger
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.socket.sendto(
            Packet.ack_packet(0), self.client_address
        )  # TODO esto no deberia estar aca

    def receive_packet(self, packet):
        # while packet:
        # packet = self.input_queue.get(True, self.TIMEOUT)

        # TODO server_socket.settimeout(SERVER_TIMEOUT) agregar timeout de cliente
        # TODO refactorizar esto para que este adentro del protocolo.
        # hay que hacer una entidad que encapsule a la cola y al socket al mismo tiempo. asi cuando hago un recv/pop desde el cliente o el worker funciona de la misma manera
        # ese pop tiene que ser bloqueante y timeouteado. la cola provee esas funcionalidades.
        try:
            if packet.finished:
                self.logger.debug(
                    f"Client: {self.client_address} finished. file saved: {packet.filename}"
                )
                self._send_ack(self.socket, self.client_address)
                self.file.close()
                return

            if packet.packet_number != self.packet_number:
                self.logger.debug(
                    f"Packet number doesnt match: recv: {packet.packet_number}, own: {self.packet_number}"
                )
                self.socket.sendto(
                    Packet.ack_packet(self.packet_number - 1), self.client_address
                )
                return  # TODO esto deberia ser un continue cuando haya hilos

            self.file.write(packet.payload)
            self.packet_number += 1
            self.logger.debug(f"Sending ACK to {self.client_address}")
            self.socket.sendto(
                Packet.ack_packet(packet.packet_number), self.client_address
            )

        except Exception as e:
            self.logger.info(e)
            self.file.close()
            os.remove(self.file.name)
            self.logger.info("exception ocurred, incomplete file removes")

    def put(self, packet):
        self.input_queue.put(packet)

    def _send_ack(self, server_socket, client_address):
        server_socket.sendto(Packet.ack_packet(0), client_address)
        self.logger.debug("ACK sent, file correctly received")
