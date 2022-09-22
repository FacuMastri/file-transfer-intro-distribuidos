import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.packet import Packet
from lib.parser import parse_upload_args

BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"


def upload_file(socket, filename, filepath, logger):
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist")
        return

    logger.info(f"Uploading {filepath} to FTP server with name {filename}")
    packets_sent = 0
    file_bytes = 0
    total_bytes = 0

    # Send data to server through socket
    with open(filepath, "rb") as file:
        data = file.read(BUFFER)
        while data:
            file_bytes += len(data)
            packets_sent += 1
            packet = Packet(packets_sent, filename, 1, 0, 0, 0, 0, 0, data)

            logger.debug(f"Sending {packet.size()} bytes to {svr_addr}")
            logger.debug(f"First 20 bytes sended: {list(packet.payload[0:20])}")

            socket.sendto(packet.to_bytes(), svr_addr)

            # client_socket.settimeout(2)
            try:
                data, client_address = socket.recvfrom(BUFFER)
            except:
                # Recibi timeout
                logging.error("Timeout event ocurr")
                exit()

            packet_rcv = Packet.from_bytes(data)

            # Revisar si llegan paquetes con timeout cumplido
            if packet_rcv.ack:
                logger.debug(f"Paquet number {packet_rcv.packet_number} ACK received")

            total_bytes += packet.size()
            # Aca habria que recibir el ACK

            data = file.read(BUFFER)
            # Aca se tiene que dar cuenta

        logger.info("Upload complete!")
        logger.info(f"Total bytes sended {total_bytes}")
        logger.info(f"Total file bytes sended {file_bytes}")
        logger.info(f"Total packets sended {packets_sent}")


if __name__ == "__main__":
    args = parse_upload_args()
    logging.basicConfig(
        format=f"[%(asctime)s] - [{COLOR_UPLOAD}upload{END_COLOR} %(levelname)s] - %(message)s",
        level=args.debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(args.debug_level)} log level")

    client_socket = socket(AF_INET, SOCK_DGRAM)
    svr_addr = (args.host, args.port)

    logging.info("FTP client up")
    logging.info(f"FTP server address {svr_addr}")
    logger = logging.getLogger(__name__)

    # Hardcodeado, como lo calculo? Tengo que abrir el archivo dos veces?
    total_packets = 100

    upload_file(client_socket, args.name, args.src, logger)
