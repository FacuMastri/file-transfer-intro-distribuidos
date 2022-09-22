import logging
from socket import AF_INET, SOCK_DGRAM, socket
from lib.packet import Packet
from lib.parser import parse_upload_args

DEFAULT_SERVER = "localhost"
DEFAULT_SERVER_PORT = 12000
DEFAULT_DEBUG_LEVEL = logging.INFO
BUFFER = 1024

if __name__ == "__main__":
    args = parse_upload_args()
    color_upload_client = "\033[0;32m"
    end_color_client = "\033[0m"
    logging.basicConfig(
        format=f"[%(asctime)s] - [{color_upload_client}upload{end_color_client} %(levelname)s] - %(message)s",
        level=args.debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(args.debug_level)} log level")

    client_socket = socket(AF_INET, SOCK_DGRAM)
    svr_addr = (args.host, args.port)

    logging.info("FTP client up")
    logging.info(f"FTP server address {svr_addr}")

    file_bytes = 0
    total_bytes = 0
    packets_sended = 0

    name = args.name
    filepath = args.src
    total_packets = (
        100  # Hardcodeado, como lo calculo? Tengo que abrir el archivo dos veces?
    )

    logging.info(f"Uploading {filepath} to FTP server with name {name}")

    with open(filepath, "rb") as f:
        data = f.read(BUFFER)
        while data:
            file_bytes += len(data)
            packets_sended += 1
            packet = Packet(packets_sended, name, 1, 0, 0, 0, 0, 0, data)

            logging.debug(f"Sending {packet.size()} bytes to {svr_addr}")
            logging.debug(f"First 20 bytes sended: {list(packet.payload[0:20])}")

            client_socket.sendto(packet.to_bytes(), svr_addr)

            client_socket.settimeout(2)
            try:
                data, client_address = client_socket.recvfrom(BUFFER)
            except:
                # Recibi timeout
                logging.error("Timeout event ocurr")
                exit()

            packet_rcv = Packet.from_bytes(data)

            # Revisar si llegan paquetes con timeout cumplido
            if packet_rcv.ack:
                logging.debug(f"Paquet number {packet_rcv.packet_number} ACK received")

            total_bytes += packet.size()
            # Aca habria que recibir el ACK

            data = f.read(BUFFER)
            # Aca se tiene que dar cuenta

    logging.info("Upload complete!")
    logging.info(f"Total bytes sended {total_bytes}")
    logging.info(f"Total file bytes sended {file_bytes}")
    logging.info(f"Total packets sended {packets_sended}")
