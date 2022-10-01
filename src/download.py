import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_download_args
from lib.stop_and_wait_manager import StopAndWaitManager, MaximumRetriesReachedError
from logger import initialize_logger
from lib.socket_wrapper import SocketWrapper

def download_file(socket: socket, filename: str, filepath: str, logger: logging.Logger):
    logger.info(f"Downloading {filename} from FTP server to {filepath}")
    input_socket = SocketWrapper(socket)
    stop_and_wait_manager = StopAndWaitManager(socket, input_socket, server_address, logger)

    stop_and_wait_manager.start_download_connection(filename)
    file = open(f"%s{filename}" % filepath, "wb")
    logger.info("connection established")

    payload = 1
    try:
        while payload:
            payload = stop_and_wait_manager.receive_data()
            logger.info(f"received payload from {server_address}")
            file.write(payload)
        file.close()
        logger.info(f"Download complete for file: {filename}!")
    except Exception as e:
        logger.info(e)
        file.close()
        os.remove(file.name)
        logger.info("exception ocurred, incomplete file removes")


if __name__ == "__main__":
    args = parse_download_args()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_address = (args.host, int(args.port))
    logger = initialize_logger(args, server_address)

    try:
        download_file(client_socket, args.name, args.dst, logger)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.info("Closing socket")
        client_socket.close()
