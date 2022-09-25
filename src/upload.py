import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_upload_args
from lib.stop_and_wait_manager import StopAndWaitManager

READ_BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"


def upload_file(socket, filename, filepath, logger):
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist")
        return
    logger.info(f"Uploading {filepath} to FTP server with name {filename}")

    stop_and_wait_manager = StopAndWaitManager(socket, svr_addr, logger)

    filesize = os.stat(filepath)
    logger.info(f"filesize {filesize.st_size}")
    stop_and_wait_manager.start_connection(filename, filesize.st_size)
    logger.info("connection established")
    packetnumber = 0
    with open(filepath, "rb") as file:
        data = file.read(READ_BUFFER)
        # TODO hay que contar los paquetes que mandamos porque podemos perder un ack del server y el server guardaria 2 veces el mismo paquete
        while data:
            stop_and_wait_manager.send_data(data, filename, packetnumber)
            data = file.read(READ_BUFFER)
            packetnumber += 1

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
    svr_addr = (args.host, args.port)

    logging.info("FTP client up")
    logging.info(f"FTP server address {svr_addr}")
    logger = logging.getLogger(__name__)

    # Hardcodeado, como lo calculo? Tengo que abrir el archivo dos veces?
    total_packets = 100
    # TODO try catch
    upload_file(client_socket, args.name, args.src, logger)
    #   TODO ver si cerrar el socket
