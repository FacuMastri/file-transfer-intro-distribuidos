import logging
import os
from socket import AF_INET, SOCK_DGRAM, socket
from lib.parser import parse_upload_args
from lib.stop_and_wait_manager import StopAndWaitManager

BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"


def upload_file(socket, filename, filepath, logger):
    if not os.path.isfile(filepath):
        logger.error(f"File {filepath} does not exist")
        return

    logger.info(f"Uploading {filepath} to FTP server with name {filename}")
    total_packets_sent = 0
    total_file_bytes = 0
    total_bytes = 0
    stop_and_wait_manager = StopAndWaitManager(socket, svr_addr, logger)

    # Send data to server through socket
    with open(filepath, "rb") as file:
        data = file.read(BUFFER)
        while data:
            total_file_bytes += len(data)
            total_packets_sent += 1
            packet_sent = stop_and_wait_manager.send_data(
                data, filename, total_packets_sent
            )
            # No se usa?
            packet_received = stop_and_wait_manager.receive_packet(BUFFER)

            total_bytes += packet_sent.size()

            data = file.read(BUFFER)

        logger.info("Upload complete!")
        logger.info(f"Total bytes sent {total_bytes}")
        logger.info(f"Total file bytes sent {total_file_bytes}")
        logger.info(f"Total packets sent {total_packets_sent}")


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

    upload_file(client_socket, args.name, args.src, logger)
