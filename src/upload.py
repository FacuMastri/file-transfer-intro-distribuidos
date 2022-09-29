import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_upload_args
from lib.stop_and_wait_manager import StopAndWaitManager, MaximumRetriesReachedError

READ_BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"


def upload_file(socket: socket, filename: str, filepath: str, logger: logging.Logger):
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist")
        return
    logger.info(f"Uploading {filepath} to FTP server with name {filename}")

    stop_and_wait_manager = StopAndWaitManager(socket, server_address, logger)

    filesize = os.stat(filepath)
    logger.info(f"filesize {filesize.st_size}")
    stop_and_wait_manager.start_connection(filename, filesize.st_size)
    logger.info("connection established")
    with open(filepath, "rb") as file:
        data = file.read(READ_BUFFER)
        while data:
            stop_and_wait_manager.send_data(data, filename)
            data = file.read(READ_BUFFER)

    stop_and_wait_manager.finish_connection(filename)
    logger.info("Upload complete!")


if __name__ == "__main__":
    args = parse_upload_args()
    logging.basicConfig(
        format=f"[%(asctime)s] - [{COLOR_UPLOAD}upload{END_COLOR} %(levelname)s] - %(message)s",
        level=args.debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(args.debug_level)} log level")

    client_socket = socket(AF_INET, SOCK_DGRAM)
    server_address = (args.host, int(args.port))

    logging.info("FTP client up")
    logging.info(f"FTP server address {server_address}")
    logger = logging.getLogger(__name__)

    try:
        upload_file(client_socket, args.name, args.src, logger)
    except MaximumRetriesReachedError:
        logger.error("Maximum retries reached")
    finally:
        logger.info("Closing socket")
        client_socket.close()
