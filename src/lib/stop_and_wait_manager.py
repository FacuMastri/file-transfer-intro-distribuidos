from lib.packet import Packet


class StopAndWaitManager:
    TIMEOUT = 200
    RETRIES = 3

    def __init__(self, socket, server_address, logger):
        self.socket = socket
        self.server_address = server_address
        self.logger = logger

    def start_connection(self, filename, filesize:int):
        packet_to_be_sent = Packet(0, 1, 0, 0, 1, 0, 0, filename, bytes(str(filesize.st_size), "utf-8")) # sending filesize as payload
        self._send_packet(packet_to_be_sent)

    def finish_connection(self, filename):
        packet_to_be_sent = Packet(0, 1, 1, 0, 0, 0, 0, filename, bytes("", "utf-8")) # sending filesize as payload
        self._send_packet(packet_to_be_sent)


    def send_data(self, data, filename):
        packet_to_be_sent = Packet(0, 1, 0, 0, 0, 0, 0, filename, data)
        self._send_packet(packet_to_be_sent)

    def _send_packet(self, packet):
        self.logger.debug(
            f"Sending {packet.size()} bytes to {self.server_address}"
        )
        self.logger.debug(
            f"First 20 bytes sent: {list(packet.payload[0:20])}"
        )
        sendcount = 0 
        # TODO validar si hay 2 acks en vuelo de recibir el ack correcto. logica en el server, validar con el sendcount
        while sendcount < self.RETRIES:
            self.socket.settimeout(self.TIMEOUT)
            try:
                self.socket.sendto(packet.to_bytes(), self.server_address)
                self.logger.info("Packet sent")
                self.receive_ack()
                self.logger.error("ACK recieved")
                return
            except:
                self.logger.error("Timeout event occurred")
                sendcount += 1

        self.logger.error("Timeout limit reached. exiting")
        self.logger.error(f"sencount {sendcount}")

        raise Exception # TODO generate own exception


    def receive_ack(self):
        packetBytes, _packetAddress = self.socket.recvfrom(Packet.HEADERSIZE)
        packet = Packet.from_bytes(packetBytes)
        self.logger.info(f"ACK recieved: {packet.ack}")
        # TODO validar que el ack paquet number coincida con el numero de paquete actual. si no coinciden se descarta el ack
        # si el cliente recibe un ack del pasado, descartarlo. es un mensaje que llego lento
        if (not packet.ack):
            raise Exception # TODO generate own exception


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
