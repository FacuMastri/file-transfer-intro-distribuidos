import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_upload_args
from lib.stop_and_wait_manager import StopAndWaitManager, MaximumRetriesReachedError
from logger import initialize_logger

def download_file(socket: socket, filename: str, filepath: str, logger: logging.Logger):
    logger.info(f"Downloading {filename} from FTP server to {filepath}")

    stop_and_wait_manager = StopAndWaitManager(socket, server_address, logger)

    file = open(f"%s{filename}" % filepath, "wb")
    stop_and_wait_manager.start_download_connection(filename)
    logger.info("connection established")
    
    finished = False
    try:
        while not finished:
            finished = stop_and_wait_manager.receive_data(filepath, file)
        file.close()
        logger.info(f"Download complete for file: {filename}!")
    except Exception as e:
        logger.info(e)
        file.close()
        os.remove(file.name)
        logger.info("exception ocurred, incomplete file removes")

if __name__ == "__main__":
    args = parse_upload_args()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_address = (args.host, int(args.port))
    logger = initialize_logger(args, server_address)

    try:
        download_file(client_socket, args.name, args.src, logger)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.info("Closing socket")
        client_socket.close()
