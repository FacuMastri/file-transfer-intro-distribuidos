import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_download_args
from lib.stop_and_wait_manager import (
    StopAndWaitManager,
)
from lib.exceptions import MaximumRetriesReachedError, OldPacketReceivedError
from logger import initialize_logger
from lib.socket_wrapper import SocketWrapper


def download_file(socket: socket, filename: str, filepath: str, logger: logging.Logger):
    logger.info(f"Downloading {filename} from FTP server to {filepath} + {filename}")
    input_socket = SocketWrapper(socket)
    stop_and_wait_manager = StopAndWaitManager(
        socket, input_socket, server_address, logger
    )

    stop_and_wait_manager.start_download_connection(filename)
    file = open(f"%s{filename}" % filepath, "wb")
    logger.info("Connection established")

    payload = 1
    while payload:
        try:
            payload = stop_and_wait_manager.receive_data()
            file.write(payload)
        except OldPacketReceivedError:
            logger.info("Old packet received, ignoring")
        except Exception as e:
            logger.info(e)
            file.close()
            os.remove(file.name)
            logger.info("Exception occurred, incomplete file removed")
            exit(-1)
    file.close()
    logger.info(f"Download complete for file: {filename}!")


if __name__ == "__main__":
    args = parse_download_args()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_address = (args.host, int(args.port))
    logger = initialize_logger(args, server_address, "download")

    try:
        download_file(client_socket, args.name, args.dst, logger)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.info("Closing socket")
        client_socket.close()
