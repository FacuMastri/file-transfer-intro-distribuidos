from socket import socket
import queue
from lib.exceptions import AckNotReceivedError, MaximumRetriesReachedError, OldPacketReceivedError
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
        packet_to_be_sent = Packet(
            0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize), "utf-8")
        )
        self._send_packet(packet_to_be_sent)

    def upload_data(self, data, filename):
        # Si hay lugar en la window, mandar el paquete
        packet = Packet(self.packet_number, 1, 0, 0, 0, 0, 0, filename, data)
        if len(self.in_flight) < self.WINDOW_SIZE:
            self._send_packet(packet)
            self.packet_number += 1
            self.logger.info(f"packet sent: {packet}")
            self.in_flight.append(packet)
            return 

        # Receive ACKs, tal vez sin la necesidad de bloquear?
        try:
            self._wait_for_ack()
        except AckNotReceivedError:
            # Manejar error
            pass

        self._send_packet(packet)
        self.packet_number += 1
        self.logger.info(f"packet sent: {packet}")
        self.in_flight.append(packet)


    def _process_ack(self, ack_packet):
        # Limpiamos de la posicion 0 a la posicion del ack, es decir, nos quedamos con los que no han sido acked
        # Puedo recibir otro paquete que no sea un ACK en esta situacion?
        for i in range(len(self.in_flight)):
            if self.in_flight[i].packet_number == ack_packet.packet_number:
                self.in_flight = self.in_flight[i + 1 :]

    def _wait_for_ack(self):
        retries = 0
        while retries != self.RETRIES:
            try:
                ack_packet = self._receive_ack()
                self._process_ack(ack_packet)
                return
            except Exception as _e:
                #TODO ver lo de las excepciones de los objetos
                # Si la lista está vacia, no hay nada que reenviar
                if not self.in_flight:
                    self.logger.info(f"window is empty, returning")
                    return
                self.logger.debug(
                    f"Timeout. Resending packets from {self.in_flight[0].packet_number}"
                )
                retries += 1
                for packet in self.in_flight:
                    self._send_packet(packet)

    def download_data(self):
        rcv_count = 0
        while rcv_count < self.RETRIES + 1:
            try:
                data, _address = self.input_stream.receive()
                break
            except Exception as _e:
                self.logger.error("Timeout event occurred on recv")
                if rcv_count == self.RETRIES + 1:
                    raise MaximumRetriesReachedError

        packet = Packet.from_bytes(data)
        self.logger.info(f"Received packet with {packet}")
        # TODO validacion de errores del packete
        if packet.is_finished():
            self.logger.debug(f"Comunication with {self.server_address} finished.")
            self.send_ack(0)
            return packet.payload
        # TODO ver si se puede mejorar el return este ^ ver que devolver en el caso de que termino
        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number does not match: recv: {packet.packet_number}, own: {self.packet_number}"
            )
            self.send_ack(self.packet_number - 1)
            raise OldPacketReceivedError
        else:
            self.send_ack(packet.packet_number)
            self.packet_number += 1
        return packet.payload
