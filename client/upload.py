import argparse
import logging
from socket import AF_INET, SOCK_DGRAM, socket

DEFAULT_SERVER = 'localhost'
DEFAULT_SERVER_PORT = 12000
DEFAULT_DEBUG_LEVEL = logging.INFO
BUFFER = 1024

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true', help="increase output verbosity")
parser.add_argument('-q', '--quiet', action='store_true', help="decrease output verbosity")
parser.add_argument('-H', '--host', metavar='host', required=False, help="service ip address")
parser.add_argument('-p', '--port', metavar='port', required=False, help="service port")
parser.add_argument('-s', '--src', metavar='path', required=True, help="source file path")
parser.add_argument('-n', '--name', metavar='path', required=False, help="file name")

args = parser.parse_args()

if args.verbose and args.quiet:
    raise ValueError('-v and -q options not compatible')

if args.quiet:
    DEBUG_LEVEL = logging.ERROR
elif args.verbose:
    DEBUG_LEVEL = logging.DEBUG
else:
    DEBUG_LEVEL = DEFAULT_DEBUG_LEVEL

SERVER = DEFAULT_SERVER if args.host is None else args.host
SERVER_PORT = DEFAULT_SERVER_PORT if args.port is None else args.port

logging.basicConfig(format='[%(levelname)s] %(message)s', level=DEBUG_LEVEL)
logging.debug(f'Setting {logging.getLevelName(DEBUG_LEVEL)} log level')

client_socket = socket(AF_INET, SOCK_DGRAM)
svr_addr = (SERVER, SERVER_PORT)

logging.info('FTP client up')
logging.info(f'FTP server address {SERVER}:{SERVER_PORT}')

with open(args.src, "rb") as f:
    logging.debug(f"Uploading {args.src} to FTP server")
    data = f.read(BUFFER)
    while(data):
        client_socket.sendto(data, svr_addr)
        data = f.read(BUFFER)
    logging.info("Upload complete!")
