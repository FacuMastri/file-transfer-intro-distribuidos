import logging

from server.parser import parse_server_args
from server.server import Server

if __name__ == "__main__":
    server_port, debug_level = parse_server_args()

    color_server = "\033[0;33m"
    end_color_server = "\033[0m"
    logging.basicConfig(
        format=f"[%(asctime)s] - [{color_server}server{end_color_server} %(levelname)s] - %(message)s",
        level=debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(debug_level)} log level")
    logger = logging.getLogger(__name__)

    server = Server("localhost", server_port, logger)
    server.start()
