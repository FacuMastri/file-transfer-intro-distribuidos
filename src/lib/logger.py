import logging

from lib.constants import COLOR_UPLOAD, END_COLOR, COLOR_DOWNLOAD, COLOR_SERVER


def initialize_logger(debug_level, server_address, action_name):

    color = COLOR_SERVER
    if action_name == "upload":
        color = COLOR_UPLOAD
    elif action_name == "download":
        color = COLOR_DOWNLOAD

    logging.basicConfig(
        format=f"[%(asctime)s] - [{color}{action_name}{END_COLOR} %(levelname)s] - %(message)s",
        level=debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(debug_level)} log level")

    logger = logging.getLogger(__name__)

    return logger
