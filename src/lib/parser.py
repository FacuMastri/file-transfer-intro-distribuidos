import argparse
import logging

DEFAULT_SERVER_PORT = 12000


def parse_server_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="decrease output verbosity"
    )
    parser.add_argument("-H", "--host", metavar="host", help="service ip address")
    parser.add_argument("-p", "--port", metavar="port", help="service port")
    parser.add_argument("-s", "--storage", metavar="path", help="storage dir path")

    args = parser.parse_args()

    if args.verbose and args.quiet:
        raise Exception("Verbose and quiet options are not compatible")

    if args.quiet:
        debug_level = logging.ERROR
    elif args.verbose:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

    server_port = DEFAULT_SERVER_PORT if args.port is None else int(args.port)

    return server_port, debug_level
