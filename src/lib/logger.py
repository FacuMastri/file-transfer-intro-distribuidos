import logging

from lib.constants import COLOR_UPLOAD, END_COLOR, COLOR_DOWNLOAD


def initialize_logger(debug_level, server_address, action):
    color = COLOR_UPLOAD if action == "upload" else COLOR_DOWNLOAD
    logging.basicConfig(
        format=f"[%(asctime)s] - [{color}{action}{END_COLOR} %(levelname)s] - %(message)s",
        level=debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(debug_level)} log level")

    logging.info("FTP client up")
    logging.info(f"FTP server address {server_address}")
    logger = logging.getLogger(__name__)

    return logger
