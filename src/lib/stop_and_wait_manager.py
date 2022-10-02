import queue
import socket

from lib.constants import RETRIES
from lib.exceptions import (
    MaximumRetriesReachedError,
    AckNotReceivedError,
    OldPacketReceivedError,
)
from lib.packet import Packet
from lib.protocol_manager import ProtocolManager


class StopAndWaitUploaderManager(ProtocolManager):
    def __init__(self, output_socket, input_stream, server_address, logger):
        super().__init__(output_socket, input_stream, server_address, logger)

    def start_upload_connection(self, filename, filesize: int):
        # Sending filesize as payload
        packet = Packet(
            0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize), "utf-8")
        )
        self._send_packet(packet)

    def upload_data(self, data, filename):
        packet = Packet(self.packet_number, 1, 0, 0, 0, 0, 0, filename, data)
        self._send_packet(packet)
        self.packet_number += 1


class StopAndWaitDownloaderManager(ProtocolManager):
    def __init__(self, output_socket, input_stream, server_address, logger):
        super().__init__(output_socket, input_stream, server_address, logger)

    def start_download_connection(self, filename):
        packet_to_be_sent = Packet(0, 0, 0, 0, 1, 0, 0, filename, bytes("", "utf-8"))
        self._send_packet(packet_to_be_sent)

    def download_data(self):
        receive_count = 0
        while receive_count < RETRIES + 1:
            try:
                data, _address = self.input_stream.receive()
                break
            except (socket.timeout, queue.Empty) as _e:
                self.logger.error("Timeout event occurred on recv")
                receive_count += 1
                if receive_count == RETRIES + 1:
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
