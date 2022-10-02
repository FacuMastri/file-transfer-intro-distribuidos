from lib.exceptions import (
    MaximumRetriesReachedError,
    AckNotReceivedError,
    OldPacketReceivedError,
)
from lib.packet import Packet


class ProtocolManager:
    TIMEOUT = 2
    RETRIES = 5
    SOCKET_BUFFER = 1024

    def __init__(self, output_socket, input_stream, server_address, logger):
        self.output_socket = output_socket
        self.input_stream = input_stream
        self.output_socket.settimeout(self.TIMEOUT)
        # entidad de entrada que encapsula a la cola bloqueante y al socket. si es un socker hace recv, si es una cola hace get(true, timeout)
        self.server_address = server_address
        self.logger = logger
        self.packet_number = 0

    def finish_connection(self, filename):
        # Sending filesize as payload
        packet_to_be_sent = Packet(0, 1, 1, 0, 0, 0, 0, filename, bytes("", "utf-8"))
        self.packet_number = 0
        try:
            self._send_packet(packet_to_be_sent)
        except Exception as _e:
            self.logger.info("Last ACK was lost, assuming connection finished.")

    def _send_packet(self, packet):
        self.logger.debug(f"Preparing {packet.size()} bytes to {self.server_address}")
        send_count = 0
        while send_count < self.RETRIES:
            try:
                self.output_socket.sendto(packet.to_bytes(), self.server_address)
                self.logger.info(f"Packet sent with ({packet})")
                self._receive_ack()
                return
            except Exception as _e:
                self.logger.error("Timeout event occurred on send")
                send_count += 1

        self.logger.error(f"Timeout limit reached. Retried {send_count} times. Exiting")

        raise MaximumRetriesReachedError

    def send_ack(self, packet_number):
        self.logger.debug(
            f"Sending ACK number {packet_number} to {self.server_address}"
        )
        self.output_socket.sendto(
            Packet.ack_packet(packet_number).to_bytes(), self.server_address
        )

    def _receive_ack(self):
        rcv_count = 0
        while rcv_count < self.RETRIES + 1:
            data, _address = self.input_stream.receive()
            packet = Packet.from_bytes(data)
            if packet.packet_number < self.packet_number:
                self.logger.debug(
                    f"Packet number does not match: recv:{packet.packet_number}, own:{self.packet_number}"
                )
                rcv_count += 1
            else:
                self.logger.info(
                    f"ACK received: {packet.is_ack()} for packet {packet.packet_number}"
                )
                return packet
        raise MaximumRetriesReachedError
