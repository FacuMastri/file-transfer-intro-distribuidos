import argparse
import logging
from multiprocessing.sharedctypes import Value
from socket import AF_INET, SOCK_DGRAM, socket

DEFAULT_DEBUG_LEVEL = logging.INFO
DEFAULT_SERVER_PORT = 12000
BUFFER = 1024

parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true', help="increase output verbosity")
parser.add_argument('-q', '--quiet', action='store_true', help="decrease output verbosity")
parser.add_argument('-H', '--host', metavar='host', required=False, help="service ip address")
parser.add_argument('-p', '--port', metavar='port', required=False, help="service port")
parser.add_argument('-s', '--storage', metavar='path', required=False, help="storage dir path")

args = parser.parse_args()

if args.verbose and args.quiet:
    raise Exception('Verbose and quiet options are not compatible')

if args.quiet:
    DEBUG_LEVEL = logging.ERROR
elif args.verbose:
    DEBUG_LEVEL = logging.DEBUG
else:
    DEBUG_LEVEL = DEFAULT_DEBUG_LEVEL

SERVER_PORT = DEFAULT_SERVER_PORT if args.port is None else int(args.port)

logging.basicConfig(format='[%(levelname)s] %(message)s', level=DEBUG_LEVEL)
logging.debug(f"Setting {logging.getLevelName(DEBUG_LEVEL)} log level")

server_socket = socket(AF_INET, SOCK_DGRAM)

try:
    server_socket.bind(('', SERVER_PORT))
except Exception as e:
    logging.error('Port already in use')
    raise e

logging.info(f'FTP server up in port {SERVER_PORT}')

data, client_address = server_socket.recvfrom(BUFFER)
f = open("server/donald.jpeg",'wb')

try:
    while(data):
        logging.debug(f"Data received from client {client_address[0]}:{client_address[1]}")
        f.write(data)
        server_socket.settimeout(2)
        data, client_address = server_socket.recvfrom(BUFFER)
except:
    f.close()
    server_socket.close()
    logging.info("File downloaded!")