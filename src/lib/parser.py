import argparse
import logging

from lib.constants import DEFAULT_SERVER_PORT, DEFAULT_SERVER_ADDRESS, DEFAULT_PROTOCOL


def make_parser(description):
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase output verbosity"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="decrease output verbosity"
    )
    parser.add_argument("-H", "--host", metavar="addr", help="server ip address")
    parser.add_argument("-p", "--port", metavar="port", help="server port")
    parser.add_argument("-P", "--prot", metavar="prot", help="server protocol")

    return parser


# TODO sacar codigo repetido
def parse_server_args():
    parser = make_parser("FTP server - flags for server command")
    parser.add_argument("-s", "--storage", metavar="dirpath", help="storage dir path")

    return get_server_args(parser.parse_args())


def parse_upload_args():
    parser = make_parser("FTP client - flags for upload command")
    parser.add_argument("-s", "--src", metavar="filepath", help="source file path")
    parser.add_argument(
        "-n", "--name", metavar="filename", required=True, help="file name"
    )

    return get_upload_args(parser.parse_args())


def get_upload_args(args):
    if args.verbose and args.quiet:
        raise Exception("Verbose and quiet options are not compatible")

    if args.quiet:
        debug_level = logging.ERROR
    elif args.verbose:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

    args.host = DEFAULT_SERVER_ADDRESS if args.host is None else args.host
    args.port = DEFAULT_SERVER_PORT if args.port is None else args.port
    args.prot = DEFAULT_PROTOCOL if args.prot is None else args.prot

    args.debug_level = debug_level

    return args


def parse_download_args():
    parser = make_parser("FTP client - flags for upload command")
    parser.add_argument("-d", "--dst", metavar="filepath", help="destination file path")
    parser.add_argument(
        "-n", "--name", metavar="filename", required=True, help="file name"
    )

    return get_download_args(parser.parse_args())


def get_download_args(args):
    if args.verbose and args.quiet:
        raise Exception("Verbose and quiet options are not compatible")

    if args.quiet:
        debug_level = logging.ERROR
    elif args.verbose:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

    args.host = DEFAULT_SERVER_ADDRESS if args.host is None else args.host
    args.port = DEFAULT_SERVER_PORT if args.port is None else args.port
    args.prot = DEFAULT_PROTOCOL if args.prot is None else args.prot

    args.debug_level = debug_level

    return args


def get_server_args(args):
    if args.verbose and args.quiet:
        raise Exception("Verbose and quiet options are not compatible")

    if args.quiet:
        debug_level = logging.ERROR
    elif args.verbose:
        debug_level = logging.DEBUG
    else:
        debug_level = logging.INFO

    args.port = DEFAULT_SERVER_PORT if args.port is None else args.port
    args.host = DEFAULT_SERVER_ADDRESS if args.host is None else args.host
    args.prot = DEFAULT_PROTOCOL if args.prot is None else args.prot

    args.debug_level = debug_level

    return args
