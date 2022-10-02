from socket import socket

from lib.exceptions import AckNotReceivedError
from lib.packet import Packet


class GoBackNManager:
    WINDOW_SIZE = 10
    TIMEOUT = 2
    RETRIES = 5

    def __init__(self, output_socket, input_stream, server_address, logger):
        self.output_socket = output_socket
        self.input_stream = input_stream
        self.server_address = server_address
        self.packet_number = 0
        self.logger = logger
        self.in_flight = []

    def _send_packet(self, packet):
        self.output_socket.sendto(packet.to_bytes(), self.server_address)
        self.logger.debug(f"Sent packet as {packet} to {self.server_address}")

    def upload_data(self, data, filename):

        packet_sent = False

        # Si hay lugar en la window, mandar el paquete
        if len(self.in_flight) < self.WINDOW_SIZE:
            packet = Packet(self.packet_number, 1, 0, 0, 0, 0, 0, filename, data)
            self._send_packet(packet)
            self.packet_number += 1
            self.in_flight.append(packet)
            packet_sent = True
        else:
            self.logger.debug("Window is full. Packet was not sent")

        # Receive ACKs, tal vez sin la necesidad de bloquear?
        try:
            ack_packet = self.receive_ack()
            self.process_ack(ack_packet)
        except AckNotReceivedError:
            # Manejar error
            pass

        # Si no mandamos el paquete, tenemos que esperar (bloquearnos) hasta que haya lugar en la window
        if not packet_sent:
            if len(self.in_flight) == self.WINDOW_SIZE:
                # Esperar por ACK
                self.wait_for_ack()

    def receive_ack(self):
        packet_bytes, _address = self.input_stream.receive()
        packet = Packet.from_bytes(packet_bytes)

        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number does not match: recv:{packet.packet_number}, own:{self.packet_number}"
            )
            self.receive_ack()

        self.logger.info(
            f"ACK received: {packet.is_ack()} for packet {packet.packet_number}"
        )
        if not packet.is_ack():
            raise AckNotReceivedError

        return packet

    def process_ack(self, ack_packet):
        # Limpiamos de la posicion 0 a la posicion del ack, es decir, nos quedamos con los que no han sido acked
        # Puedo recibir otro paquete que no sea un ACK en esta situacion?
        for i in range(len(self.in_flight)):
            if self.in_flight[i].packet_number == ack_packet.packet_number:
                self.in_flight = self.in_flight[i + 1 :]

    def wait_for_ack(self):
        retries = 0
        try:
            ack_packet = self.receive_ack()
            self.process_ack(ack_packet)
        except socket.timeout:
            # Si la lista está vacia, no hay nada que reenviar
            if not self.in_flight:
                return
            self.logger.debug(
                f"Timeout. Resending packets from {self.in_flight[0].packet_number}"
            )
            retries += 1
            for packet in self.in_flight:
                self._send_packet(packet)
