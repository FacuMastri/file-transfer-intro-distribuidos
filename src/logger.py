import logging

READ_BUFFER = 1024
# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"

def initialize_logger(args, server_address):
    logging.basicConfig(
        format=f"[%(asctime)s] - [{COLOR_UPLOAD}upload{END_COLOR} %(levelname)s] - %(message)s",
        level=args.debug_level,
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.debug(f"Setting {logging.getLevelName(args.debug_level)} log level")
    
    logging.info("FTP client up")
    logging.info(f"FTP server address {server_address}")
    logger = logging.getLogger(__name__)
    return logger
