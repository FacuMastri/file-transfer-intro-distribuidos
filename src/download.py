import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket

from lib.constants import SAW_PROTOCOL
from lib.go_back_n_manager import GoBackNManager
from lib.parser import parse_download_args
from lib.stop_and_wait_manager import (
    StopAndWaitDownloaderManager,
    MaximumRetriesReachedError,
    OldPacketReceivedError,
)
from lib.logger import initialize_logger
from lib.socket_wrapper import SocketWrapper


def download_file(
    socket: socket,
    file_name: str,
    file_path: str,
    logger: logging.Logger,
    protocol: str,
):
    logger.info(f"Downloading {file_name} from FTP server to {file_path} + {file_name}")
    input_socket = SocketWrapper(socket)
    downloader = (
        StopAndWaitDownloaderManager(socket, input_socket, server_address, logger)
        if protocol == SAW_PROTOCOL
        else GoBackNManager(socket, input_socket, server_address, logger)
    )

    logger.info("FTP client up")
    downloader.start_download_connection(file_name)
    file = open(f"%s{file_name}" % file_path, "wb")
    logger.info("Connection established")

    payload = 1
    while payload:
        try:
            payload = downloader.download_data()
            file.write(payload)
        except OldPacketReceivedError:
            logger.debug("Old packet received, ignoring")
        except MaximumRetriesReachedError as e:
            file.close()
            os.remove(file_path + file_name)
            logger.info(f"Exception occurred: {e}, incomplete file removed")
            exit(-1)
    file.close()
    logger.info(
        f"Download completed for file: {file_name}! It was saved to {file_path + file_name}"
    )


if __name__ == "__main__":
    args = parse_download_args()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_address = (args.host, int(args.port))
    logger = initialize_logger(args.debug_level, server_address, "download")

    try:
        download_file(client_socket, args.name, args.dst, logger, args.prot)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.debug("Closing socket")
        client_socket.close()
