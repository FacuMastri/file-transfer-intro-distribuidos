from lib.packet import Packet


class StopAndWaitManager:
    TIMEOUT = 5

    def __init__(self, socket, server_address, logger):
        self.socket = socket
        self.server_address = server_address
        self.logger = logger

    def send_data(self, data, filename, packet_number):
        packet_to_be_sent = Packet(packet_number, filename, 1, 0, 0, 0, 0, 0, data)
        self.logger.debug(
            f"Sending {packet_to_be_sent.size()} bytes to {self.server_address}"
        )
        self.logger.debug(
            f"First 20 bytes sent: {list(packet_to_be_sent.payload[0:20])}"
        )
        self.socket.sendto(packet_to_be_sent.to_bytes(), self.server_address)
        # Lo devuelvo solo para cumplir con la interfaz de quien llama a este metodo (o sea para poder contar los bytes
        # enviados en modo debug)
        return packet_to_be_sent

    def receive_packet(self, socket_buffer_size):
        # self.socket.settimeout(2)
        try:
            data, client_address = self.socket.recvfrom(socket_buffer_size)
        except:
            # Recibi timeout
            # TODO Aca habria que hacer la logica de reenviar el paquete
            self.logger.error("Timeout event occurred")
            exit()

        packet_received = Packet.from_bytes(data)
        # Revisar si llegan paquetes con timeout cumplido
        if packet_received.ack:
            self.logger.debug(
                f"Packet number {packet_received.packet_number} ACK received"
            )

        return packet_received
        # Aca habria que recibir el ACK

        def stop(self):
            raise NotImplementedError
