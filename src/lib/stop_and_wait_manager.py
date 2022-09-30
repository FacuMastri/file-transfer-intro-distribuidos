import os
from tkinter import E
from lib.packet import Packet


class MaximumRetriesReachedError(Exception):
    pass


class AckNotReceivedError(Exception):
    pass


class StopAndWaitManager:
    TIMEOUT = 2
    RETRIES = 3
    SOCKET_BUFFER = 1024

    def __init__(self, socket, server_address, logger):
        self.socket = socket
        # entidad de entrada que encapsula a la cola bloqueante y al socket. si es un socker hace recv, si es una cola hace get(true, timeout)
        self.server_address = server_address
        self.logger = logger
        self.packet_number = 0

    def start_upload_connection(self, filename, filesize: int):
        packet_to_be_sent = Packet(
            0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize), "utf-8")
        )  # sending filesize as payload
        self._send_packet(packet_to_be_sent)

    def start_download_connection(self, filename):
        packet_to_be_sent = Packet(
            0, 0, 0, 0, 1, 0, 0, filename, bytes("", "utf-8")
        )
        self._send_packet(packet_to_be_sent)

    def finish_upload_connection(self, filename):
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
        send_count = 0
        while send_count < self.RETRIES:
            self.socket.settimeout(self.TIMEOUT)
            try:
                self.socket.sendto(packet.to_bytes(), self.server_address)
                self.logger.info(f"Packet sent with ({packet})")
                self.receive_ack()
                return
            except:
                self.logger.error("Timeout event occurred")
                send_count += 1

        self.logger.error("Timeout limit reached. Exiting")
        self.logger.error(f"Send count: {send_count}")

        raise MaximumRetriesReachedError

    def receive_data(self, file):
        data = self.socket.recvfrom(self.SOCKET_BUFFER)[0]
        packet = Packet.from_bytes(data)
        
        if packet.is_finished():
            self.send_ack(self, 0)
            return True

        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number doesnt match: recv: {packet.packet_number}, own: {self.packet_number}"
            )
            self.send_ack(self, self.packet_number - 1)
        else:
            file.write(packet.payload)
            self.packet_number += 1
            self.send_ack(self, packet.packet_number)
        return False

    def send_ack(self, packet_number):
        self.logger.debug(f"Sending ACK to server")
        self.socket.sendto(Packet.ack_packet(packet_number).to_bytes(), self.server_address)

    def receive_ack(self):

        packet_bytes, _packet_address = self.socket.recvfrom(Packet.HEADER_SIZE)
        packet = Packet.from_bytes(packet_bytes)

        if packet.packet_number != self.packet_number:
            self.logger.debug(
                f"Packet number doesnt match: recv:{packet.packet_number}, own:{self.packet_number}"
            )
            self.receive_ack()

        self.logger.info(f"ACK received: {packet.is_ack()}")
        if not packet.is_ack():
            raise AckNotReceivedError
