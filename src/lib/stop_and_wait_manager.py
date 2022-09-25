from asyncio import current_task
from black import re_compile_maybe_verbose
from lib.packet import Packet


class StopAndWaitManager:
    TIMEOUT = 2
    RETRIES = 3

    def __init__(self, socket, server_address, logger):
        self.socket = socket
        self.server_address = server_address
        self.logger = logger
        self.packet_number = 0

    def start_connection(self, filename, filesize: int):
        packet_to_be_sent = Packet(
            0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize), "utf-8")
        )  # sending filesize as payload
        self._send_packet(packet_to_be_sent)

    def finish_connection(self, filename):
        packet_to_be_sent = Packet(
            0, 1, 1, 0, 0, 0, 0, filename, bytes("", "utf-8")
        )  # sending filesize as payload
        self.packet_number = 0
        self._send_packet(packet_to_be_sent)

    def send_data(self, data, filename):
        packet_to_be_sent = Packet(self.packet_number, 1, 0, 0, 0, 0, 0, filename, data)
        self._send_packet(packet_to_be_sent)
        self.packet_number += 1

    def _send_packet(self, packet):
        self.logger.debug(f"Sending {packet.size()} bytes to {self.server_address}")
        self.logger.debug(f"First 20 bytes sent: {list(packet.payload[0:20])}")
        send_count = 0
        while send_count < self.RETRIES:
            self.socket.settimeout(self.TIMEOUT)
            try:
                self.socket.sendto(packet.to_bytes(), self.server_address)
                self.logger.info("Packet sent")
                self.receive_ack()
                self.logger.info("ACK received")
                return
            except:
                self.logger.error("Timeout event occurred")
                send_count += 1

        self.logger.error("Timeout limit reached. exiting")
        self.logger.error(f"send count {send_count}")

        raise Exception  # TODO generate own exception

    def receive_ack(self):

        packet_bytes, _packet_address = self.socket.recvfrom(Packet.HEADER_SIZE)
        packet = Packet.from_bytes(packet_bytes)

        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number doesnt match: recv:{packet.packet_number}, own:{self.packet_number}"
            )
            self.receive_ack()

        self.logger.info(f"ACK received: {packet.ack}")
        if not packet.ack:
            raise Exception  # TODO generate own exception

    def stop(self):
        raise NotImplementedError
