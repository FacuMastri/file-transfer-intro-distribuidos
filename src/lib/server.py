import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.packet import Packet

BUCKET_DIRECTORY = "src/server/files/"

SOCKET_BUFFER = 4096


class Server:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def start(self):
        if not os.path.exists("%s" % BUCKET_DIRECTORY):
            os.makedirs(BUCKET_DIRECTORY) 
        server_socket = self._create_socket()
        self.logger.info(f"FTP server up in port {self.port}")

        while True:
            server_socket.settimeout(100000)
            data, client_address = self._receive_filesize(server_socket)
            #  TODO verificar que hay suficiente espacio en disco para el archivo

            # TODO cola de mensajes para manejar multiples clientes
            self.logger.info(f"Received data from {client_address}")
            packet = Packet.from_bytes(data)
            self.logger.debug(f"Filename received: {packet.filename}")

            file = open(f"%s{packet.filename}" % BUCKET_DIRECTORY, "wb")

            packetscount = 0

            try:
                while data:
                    data, client_address = server_socket.recvfrom(SOCKET_BUFFER)
                    # TODO validar que el numero de paquete es el siguiente. si es el mismo que el actual mandar un ack
                    packet = Packet.from_bytes(data)
                    self.logger.debug(
                        f"Data received from client {client_address}: {len(data)} bytes"
                    )
                    if (packet.finished):
                        self.logger.debug(f"Client: {client_address} finished. file saved: {packet.filename}")
                        self._send_ack(server_socket, client_address)
                        file.close()
                        break

                    if (packet.packet_number != packetscount):
                        self.logger.debug(f"Packet number doesnt match: {packet.packet_number}, {packetscount}")
                        continue

                    file.write(packet.payload)
                    self.logger.debug(f"Sending ACK to  {client_address}")
                    server_socket.sendto(Packet.ack_packet(packet.packet_number), client_address)
                    packetscount += 1

            except:
                file.close()
                self.logger.info("File downloaded!")
                self.logger.info(f"Total packets received: {packetscount}")

    def _receive_filesize(self, server_socket):
        data, client_address = server_socket.recvfrom(SOCKET_BUFFER)
        # TODO cola de mensajes para manejar multiples clientes
        self.logger.info(f"Received first message from {client_address}")
        packet = Packet.from_bytes(data)
        self.logger.debug(f"Filesize received: {packet.payload}")
        self._send_ack(server_socket, client_address)

        return data, client_address

    def _send_ack(self, server_socket, client_address):
        server_socket.sendto(Packet.ack_packet(0), client_address)
        self.logger.debug("ACK sent")

    def _create_socket(self):
        server_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            server_socket.bind((self.host, self.port))
        except Exception as e:
            self.logger.error("Port already in use")
            raise e
        return server_socket

    def stop(self):
        raise NotImplementedError()

    def listen_for_connections(self):
        raise NotImplementedError()
