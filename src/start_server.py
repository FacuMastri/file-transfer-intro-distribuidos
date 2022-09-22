import logging

from lib.parser import parse_server_args
from lib.server import Server

# Orange
COLOR_SERVER = "\033[0;33m"
END_COLOR = "\033[0m"

if __name__ == "__main__":
    server_port, debug_level = parse_server_args()

    logging.basicConfig(
        format=f"[%(asctime)s] - [{COLOR_SERVER}server{END_COLOR} %(levelname)s] - %(message)s",
        level=debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(debug_level)} log level")
    logger = logging.getLogger(__name__)

    server = Server("localhost", server_port, logger)
    server.start()
