import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_upload_args
from lib.socket_wrapper import SocketWrapper
from lib.stop_and_wait_manager import (
    StopAndWaitUploaderManager,
    MaximumRetriesReachedError,
)
from lib.logger import initialize_logger
from lib.constants import SAW_PROTOCOL, READ_BUFFER
from lib.go_back_n_manager import GoBackNManager

# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"


def upload_file(
    socket: socket, filename: str, filepath: str, logger: logging.Logger, protocol: str
):
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist")
        return

    logger.info(f"Uploading {filepath} to FTP server with name {filename}")
    input_socket = SocketWrapper(socket)
    uploader = (
        StopAndWaitUploaderManager(socket, input_socket, server_address, logger)
        if protocol == SAW_PROTOCOL
        else GoBackNManager(socket, input_socket, server_address, logger)
    )

    filesize = os.stat(filepath)
    logger.info(f"filesize {filesize.st_size}")
    uploader.start_upload_connection(filename, filesize.st_size)
    logger.info("Connection established")
    with open(filepath, "rb") as file:
        data = file.read(READ_BUFFER)
        while data:
            uploader.upload_data(data, filename)
            data = file.read(READ_BUFFER)

    uploader.finish_connection(filename)
    logger.info("Upload complete!")


if __name__ == "__main__":
    args = parse_upload_args()
    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_address = (args.host, int(args.port))
    logger = initialize_logger(args.debug_level, server_address, "upload")

    try:
        upload_file(client_socket, args.name, args.src, logger, args.prot)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.info("Closing socket")
        client_socket.close()
