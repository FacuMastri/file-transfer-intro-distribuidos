import argparse
import logging
from socket import AF_INET, SOCK_DGRAM, socket
from lib.packet import Packet

DEFAULT_SERVER = "localhost"
DEFAULT_SERVER_PORT = 12000
DEFAULT_DEBUG_LEVEL = logging.INFO
BUFFER = 1024

parser = argparse.ArgumentParser(description="FTP server - flags for upload command")

parser.add_argument(
    "-v", "--verbose", action="store_true", help="increase output verbosity"
)
parser.add_argument(
    "-q", "--quiet", action="store_true", help="decrease output verbosity"
)
parser.add_argument("-H", "--host", metavar="addr", help="server ip address")
parser.add_argument("-p", "--port", metavar="port", help="server port")
parser.add_argument("-s", "--src", metavar="filepath", help="source file path")
parser.add_argument("-n", "--name", metavar="filename", required=True, help="file name")

args = parser.parse_args()

if args.verbose and args.quiet:
    raise ValueError("-v and -q options not compatible")

if args.quiet:
    DEBUG_LEVEL = logging.ERROR
elif args.verbose:
    DEBUG_LEVEL = logging.DEBUG
else:
    DEBUG_LEVEL = DEFAULT_DEBUG_LEVEL

SERVER = DEFAULT_SERVER if args.host is None else args.host
SERVER_PORT = DEFAULT_SERVER_PORT if args.port is None else args.port

color_upload_client = "\033[0;32m"
end_color_client = "\033[0m"
logging.basicConfig(
    format=f"[%(asctime)s] - [{color_upload_client}upload{end_color_client} %(levelname)s] - %(message)s",
    level=DEBUG_LEVEL,
    datefmt="%Y/%m/%d %H:%M:%S",
)
logging.debug(f"Setting {logging.getLevelName(DEBUG_LEVEL)} log level")

client_socket = socket(AF_INET, SOCK_DGRAM)
svr_addr = (SERVER, SERVER_PORT)

logging.info("FTP client up")
logging.info(f"FTP server address {SERVER}:{SERVER_PORT}")

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

        logging.debug(f"Sending {packet.size()} bytes to {SERVER}:{SERVER_PORT}")
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
