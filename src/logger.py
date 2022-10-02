import logging

READ_BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"
# Blue
COLOR_DOWNLOAD = "\033[0;34m"


def initialize_logger(args, server_address, action):
    color = COLOR_UPLOAD if action == "upload" else COLOR_DOWNLOAD
    logging.basicConfig(
        format=f"[%(asctime)s] - [{color}{action}{END_COLOR} %(levelname)s] - %(message)s",
        level=args.debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(args.debug_level)} log level")

    logging.info("FTP client up")
    logging.info(f"FTP server address {server_address}")
    logger = logging.getLogger(__name__)
    return logger
