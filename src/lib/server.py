from socket import AF_INET, SOCK_DGRAM, socket
from lib.packet import Packet

BUFFER = 4096


class Server:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger

    def start(self):
        server_socket = socket(AF_INET, SOCK_DGRAM)
        try:
            server_socket.bind((self.host, self.port))
        except Exception as e:
            self.logger.error("Port already in use")
            raise e
        self.logger.info(f"FTP server up in port {self.port}")

        data, client_address = server_socket.recvfrom(BUFFER)
        # TODO cola de mensajes para manejar multiples clientes
        self.logger.info(f"Received first message from {client_address}")
        packet = Packet.from_bytes(data)
        self.logger.debug(f"Filsize received: {packet.payload}")

        server_socket.sendto(Packet.ack_packet(), client_address)
        self.logger.debug(f"ACK sent")


        while True:
            server_socket.settimeout(100000) # TODO ver si sigue estando esto
            data, client_address = server_socket.recvfrom(BUFFER)
            # TODO cola de mensajes para manejar multiples clientes
            self.logger.info(f"Received data from {client_address}")
            packet = Packet.from_bytes(data)
            self.logger.debug(f"Filename received: {packet.filename}")
            #  TODO verificar que el archivo entra
            file = open(f"src/server/files/{packet.filename}", "wb")

            total_bytes_written = 0
            total_bytes_received = 0
            total_packets = 0

            try:
                while data:
                    total_bytes_received += len(data)
                    total_packets += 1
                    self.logger.debug(
                        f"Data received from client {client_address[0]}:{client_address[1]}: {len(data)} bytes"
                    )
                    self.logger.debug(f"First 20 bytes received: {list(data[0:20])}")

                    file.write(packet.payload)
                    self.logger.debug(
                        f"Sending ACK to  {client_address}"
                    )
                    server_socket.sendto(Packet.ack_packet(), client_address)
                    total_bytes_written += len(packet.payload)

                    self.logger.debug(
                        f"Writting data to {file.name}: {len(packet.payload)} bytes"
                    )
                    self.logger.debug(
                        f"First 20 bytes written: {list(packet.payload[0:20])}"
                    )

                    server_socket.settimeout(2)
                    data, client_address = server_socket.recvfrom(BUFFER)
                    # TODO validar que el numero de paquete es el siguiente. si es el mismo que el actual mandar un ack
                    packet = Packet.from_bytes(data)

            except:
                file.close()
                self.logger.info("File downloaded!")
                self.logger.info(f"Total bytes received: {total_bytes_received}")
                self.logger.info(f"Total bytes written in disk: {total_bytes_written}")
                self.logger.info(f"Total packets received: {total_packets}")

    def stop(self):
        raise NotImplementedError()

    def listen_for_connections(self):
        raise NotImplementedError()
