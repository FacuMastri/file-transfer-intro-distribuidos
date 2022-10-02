from lib.exceptions import (
    MaximumRetriesReachedError,
    AckNotReceivedError,
    OldPacketReceivedError,
)
from lib.packet import Packet


class StopAndWaitManager:
    TIMEOUT = 2
    RETRIES = 5
    SOCKET_BUFFER = 1024

    def __init__(self, output_socket, input_stream, server_address, logger):
        self.output_socket = output_socket
        self.input_stream = input_stream
        # entidad de entrada que encapsula a la cola bloqueante y al socket. si es un socker hace recv, si es una cola hace get(true, timeout)
        self.server_address = server_address
        self.logger = logger
        self.packet_number = 0

    def finish_connection(self, filename):
        packet_to_be_sent = Packet(
            0, 1, 1, 0, 0, 0, 0, filename, bytes("", "utf-8")
        )  # sending filesize as payload
        self.packet_number = 0
        self._send_packet(packet_to_be_sent)

    def _send_packet(self, packet):
        self.logger.debug(f"Preparing {packet.size()} bytes to {self.server_address}")
        send_count = 0
        while send_count < self.RETRIES:
            self.input_stream.settimeout(self.TIMEOUT)
            try:
                self.output_socket.sendto(packet.to_bytes(), self.server_address)
                self.logger.info(f"Packet sent with ({packet})")
                self.receive_ack()
                return
            except Exception as _e:
                self.logger.error("Timeout event occurred")
                send_count += 1

        self.logger.error(f"Timeout limit reached. Retried {send_count} times. Exiting")

        raise MaximumRetriesReachedError

    def send_ack(self, packet_number):
        self.logger.debug(f"Sending ACK number {packet_number} to {self.server_address}")
        self.output_socket.sendto(
            Packet.ack_packet(packet_number).to_bytes(), self.server_address
        )

    def receive_ack(self):

        packet_bytes, _address = self.input_stream.receive()
        packet = Packet.from_bytes(packet_bytes)

        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number doesnt match: recv:{packet.packet_number}, own:{self.packet_number}"
            )
            self.receive_ack()

        self.logger.info(f"ACK received: {packet.is_ack()}")
        if not packet.is_ack():
            raise AckNotReceivedError


class StopAndWaitUploaderManager(StopAndWaitManager):
    def __init__(self, output_socket, input_stream, server_address, logger):
        super().__init__(output_socket, input_stream, server_address, logger)

    def start_upload_connection(self, filename, filesize: int):
        packet_to_be_sent = Packet(
            0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize), "utf-8")
        )  # sending filesize as payload
        self._send_packet(packet_to_be_sent)

    def upload_data(self, data, filename):
        packet_to_be_sent = Packet(self.packet_number, 1, 0, 0, 0, 0, 0, filename, data)
        self._send_packet(packet_to_be_sent)
        self.packet_number += 1


class StopAndWaitDownloaderManager(StopAndWaitManager):
    def __init__(self, output_socket, input_stream, server_address, logger):
        super().__init__(output_socket, input_stream, server_address, logger)

    def start_download_connection(self, filename):
        packet_to_be_sent = Packet(0, 0, 0, 0, 1, 0, 0, filename, bytes("", "utf-8"))
        self._send_packet(packet_to_be_sent)

    def download_data(self):
        self.input_stream.settimeout(self.TIMEOUT)
        rcv_count = 0
        while rcv_count < self.RETRIES + 1:
            try:
                data, _address = self.input_stream.receive()
                break
            except Exception as _e:

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
                f"Packet number doesnt match: recv: {packet.packet_number}, own: {self.packet_number}"
            )
            self.send_ack(self.packet_number - 1)
            raise OldPacketReceivedError
        else:
            self.send_ack(packet.packet_number)
            self.packet_number += 1

        return packet.payload

    def send_ack(self, packet_number):
        self.logger.debug(
            f"Sending ACK number {packet_number} to {self.server_address}"
        )
        self.output_socket.sendto(
            Packet.ack_packet(packet_number).to_bytes(), self.server_address
        )

    def receive_ack(self):

        packet_bytes, _address = self.input_stream.receive()
        packet = Packet.from_bytes(packet_bytes)

        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number does not match: recv: {packet.packet_number}, own: {self.packet_number}"
            )
            self.receive_ack()

        self.logger.info(
            f"ACK received: {packet.is_ack()} for packet {packet.packet_number}"
        )
        if not packet.is_ack():
            raise AckNotReceivedError
