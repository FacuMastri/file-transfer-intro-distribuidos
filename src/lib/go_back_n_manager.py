import queue
import socket

from lib.constants import RETRIES
from lib.exceptions import (
    AckNotReceivedError,
    MaximumRetriesReachedError,
    OldPacketReceivedError,
)
from lib.packet import Packet
from lib.protocol_manager import ProtocolManager


class GoBackNManager(ProtocolManager):
    WINDOW_SIZE = 10

    def __init__(self, output_socket, input_stream, server_address, logger):
        super().__init__(output_socket, input_stream, server_address, logger)
        self.in_flight = []
        self.packet_to_be_sent = None

    def _send_packet(self, packet):
        self.output_socket.sendto(packet.to_bytes(), self.server_address)
        self.logger.debug(f"Sent packet as {packet} to {self.server_address}")

    def start_upload_connection(self, filename, filesize: int):
        # Sending filesize as payload
        packet = Packet(0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize), "utf-8"))
        self._send_packet(packet)

    def start_download_connection(self, filename):
        packet = Packet(0, 0, 0, 0, 1, 0, 0, filename, bytes("", "utf-8"))
        super()._send_packet(packet)

    def finish_connection(self, filename):
        while self._wait_for_ack():
            pass
        # Sending filesize as payload
        packet_to_be_sent = Packet(0, 1, 1, 0, 0, 0, 0, filename, bytes("", "utf-8"))
        self.packet_number = 0
        try:
            super()._send_packet(packet_to_be_sent)
        except MaximumRetriesReachedError:
            self.logger.debug("Last ACK was lost, assuming connection finished.")

    def upload_data(self, data, filename):

        packet_number = 0
        if self.in_flight:
            packet_number = self.in_flight[-1].packet_number + 1

        packet = Packet(packet_number, 1, 0, 0, 0, 0, 0, filename, data)
        self.logger.debug(f"In flight len: {len(self.in_flight)}")

        # Si hay lugar en la window, mandar el paquete
        if len(self.in_flight) < self.WINDOW_SIZE:
            self._send_packet(packet)
            self.in_flight.append(packet)
            return

        # Esperamos que llegue un ACK para liberar espacio en la window y enviamos el paquete
        self._wait_for_ack()
        self._send_packet(packet)
        self.in_flight.append(packet)

    def _process_ack(self, ack_packet):
        # Esto puede dar negativo -> entonces no popea la lista nunca y ahi la in flight crece de tamaño
        # mas alla del window size
        packet_received = ack_packet.packet_number - self.in_flight[0].packet_number
        # Fix para el ultimo paquete de desconexion
        if packet_received == 0:
            self.in_flight.pop(0)
        for i in range(packet_received):
            self.in_flight.pop(0)
        # Esto en la ultima iteracion explota, por eso el try/catch en el _wait_for_ack
        # con el IndexError
        self.packet_number = self.in_flight[0].packet_number

    def _wait_for_ack(self):
        retries = 0
        while retries != RETRIES:
            try:
                ack_packet = self._receive_ack()
                self._process_ack(ack_packet)
                if not self.in_flight:
                    self.logger.debug("Window is empty, returning")
                    return False
                return True
            except (socket.timeout, queue.Empty, IndexError) as _e:
                # Si la lista está vacia, no hay nada que reenviar
                if not self.in_flight:
                    self.logger.debug("Window is empty, returning")
                    return False
                self.logger.debug(
                    f"Timeout. Resending packets from packet number {self.in_flight[0].packet_number}"
                )
                retries += 1
                for packet in self.in_flight:
                    self._send_packet(packet)
        raise MaximumRetriesReachedError

    def download_data(self):
        rcv_count = 0
        while rcv_count < RETRIES + 1:
            try:
                data, _address = self.input_stream.receive()
                break
            except (socket.timeout, queue.Empty) as _e:
                self.logger.debug("Timeout event occurred on recv")
                rcv_count += 1
                if rcv_count == RETRIES + 1:
                    raise MaximumRetriesReachedError
            

        packet = Packet.from_bytes(data)
        self.logger.debug(f"Received packet as {packet}")
        if packet.is_finished():
            self.logger.debug(f"Comunication with {self.server_address} finished.")
            self.send_ack(0)
            return packet.payload
        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number does not match: recv: {packet.packet_number}, own: {self.packet_number}"
            )
            if self.packet_number == 0:
                raise OldPacketReceivedError
            self.send_ack(self.packet_number - 1)
            raise OldPacketReceivedError
        else:
            self.send_ack(packet.packet_number)
            self.packet_number += 1
        return packet.payload
