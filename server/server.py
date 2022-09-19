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
name = data[0:11]
logging.debug(f"Filename received: {name.decode()}")

file = open(f"server/{name.decode()}",'wb')

total_bytes_written = 0
total_bytes_received = 0
total_packets = 0

def process_packet(data, header_bytes):
    header = data[0:header_bytes]
    data = data[header_bytes:]
    return header, data

try:
    while(data):
        total_bytes_received += len(data)
        total_packets += 1
        logging.debug(f"Data received from client {client_address[0]}:{client_address[1]}: {len(data)} bytes")
        logging.debug(f"First 20 bytes received: {list(data[0:20])}")
        
        # Aqui puedo extraer los datos del archivo del paquete recibido
        header, data = process_packet(data, 11) # Aca extraigo headers y cosas asi que vayamos definiendo
        file.write(data)
        total_bytes_written += len(data)

        logging.debug(f"Writting data to {file.name}: {len(data)} bytes")
        logging.debug(f"First 20 bytes written: {list(data[0:20])}")
        
        server_socket.settimeout(2)
        data, client_address = server_socket.recvfrom(BUFFER)
        
except:
    file.close()
    server_socket.close()
    logging.info("File downloaded!")
    logging.info(f"Total bytes received: {total_bytes_received}")
    logging.info(f"Total bytes written in disk: {total_bytes_written}")
    logging.info(f"Total packets received: {total_packets}")