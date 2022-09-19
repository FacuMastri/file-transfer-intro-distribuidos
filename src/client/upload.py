import argparse
import logging
from socket import AF_INET, SOCK_DGRAM, socket
from utils import construct_packet

DEFAULT_SERVER = "localhost"
DEFAULT_SERVER_PORT = 12000
DEFAULT_DEBUG_LEVEL = logging.INFO
BUFFER = 1024

parser = argparse.ArgumentParser()

parser.add_argument(
    "-v", "--verbose", action="store_true", help="increase output verbosity"
)
parser.add_argument(
    "-q", "--quiet", action="store_true", help="decrease output verbosity"
)
parser.add_argument("-H", "--host", metavar="host", help="service ip address")
parser.add_argument("-p", "--port", metavar="port", help="service port")
parser.add_argument("-s", "--src", metavar="path", help="source file path")
parser.add_argument("-n", "--name", metavar="path", required=True, help="file name")

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

logging.basicConfig(format="[%(levelname)s] %(message)s", level=DEBUG_LEVEL)
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
        packet = construct_packet(packets_sended, name, total_packets, data)

        logging.debug(f"Sending {len(packet)} bytes to {SERVER}:{SERVER_PORT}")
        logging.debug(f"First 20 bytes sended: {list(packet[0:20])}")

        client_socket.sendto(packet, svr_addr)
        total_bytes += len(packet)

        data = f.read(BUFFER)

    logging.info("Upload complete!")

    logging.info(f"Total bytes sended {total_bytes}")
    logging.info(f"Total file bytes sended {file_bytes}")
    logging.info(f"Total packets sended {packets_sended}")
