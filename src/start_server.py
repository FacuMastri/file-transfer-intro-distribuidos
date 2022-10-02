import logging

from lib.parser import parse_server_args
from lib.server import Server

# Orange
COLOR_SERVER = "\033[0;33m"
END_COLOR = "\033[0m"

if __name__ == "__main__":
    args = parse_server_args()

    logging.basicConfig(
        format=f"[%(asctime)s] - [{COLOR_SERVER}server{END_COLOR} %(levelname)s] - %(message)s",
        level=args.debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(args.debug_level)} log level")
    logger = logging.getLogger(__name__)

    server = Server(args.host, int(args.port), logger)
    try:
        server.start(args.prot)
    except:
        logger.error("Unexpected exception caught, exiting...")
