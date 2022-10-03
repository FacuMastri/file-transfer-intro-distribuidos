from lib.logger import initialize_logger
from lib.parser import parse_server_args
from lib.server import Server

if __name__ == "__main__":

    args = parse_server_args()
    logger = initialize_logger(args.debug_level, (args.host, args.port), "server")

    server = Server(args.host, int(args.port), logger)

    try:
        server.start(args.prot, args.storage)
    except Exception as e:
        logger.error(f"Unexpected exception caught: {e}, exiting...")
