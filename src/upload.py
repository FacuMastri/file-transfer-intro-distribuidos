import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_upload_args
from lib.socket_wrapper import SocketWrapper
from lib.stop_and_wait_manager import StopAndWaitUploaderManager, MaximumRetriesReachedError
from logger import initialize_logger

READ_BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"


def upload_file(socket: socket, filename: str, filepath: str, logger: logging.Logger):
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist")
        return

    logger.info(f"Uploading {filepath} to FTP server with name {filename}")
    input_socket = SocketWrapper(socket)
    uploader = StopAndWaitUploaderManager(socket, input_socket, server_address, logger)

    filesize = os.stat(filepath)
    logger.info(f"filesize {filesize.st_size}")
    uploader.start_upload_connection(filename, filesize.st_size)
    logger.info("connection established")
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
    logger = initialize_logger(args, server_address, "upload")

    try:
        upload_file(client_socket, args.name, args.src, logger)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.info("Closing socket")
        client_socket.close()
