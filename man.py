from fabric import Connection

import getpass
import argparse

from nodes import *

def make_conn(host, pubkey=False, password=None):
    if not pubkey and password is None:
        password = getpass.getpass("Password for connection to {}: ".format(host))

    return Connection(host, connect_kwargs={ "password": password })

def host_args(parser):
    parser.add_argument("host", nargs="+", help="[user@]<host>")
    parser.add_argument("--use-pubkey", action="store_const", const=True,
                        help="Use public key instead of asking for password")

def cmd_install_master(args):
    for host in args.host:
        conn = make_conn(host, pubkey=args.use_pubkey)
        master = Master(conn)
        master.setup()

def cmd_install_worker(args):
    for host in args.host:
        conn = make_conn(host, pubkey=args.use_pubkey)
        worker = Worker(conn)
        worker.setup(args.master_host, args.master_port, args.token)

def cmd_stop_master(args):
    for host in args.host:
        conn = make_conn(host, pubkey=args.use_pubkey)
        master = Master(conn)
        master.stop()

def cmd_stop_worker(args):
    for host in args.host:
        conn = make_conn(host, pubkey=args.use_pubkey)
        worker = Worker(conn)
        worker.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Broadway nodes")
    parser.set_defaults(handler=lambda _: parser.print_help())

    parser_sub = parser.add_subparsers()

    # -> install
    parser_install = parser_sub.add_parser("install")
    parser_install.set_defaults(handler=lambda _: parser_install.print_help())

    parser_install_sub = parser_install.add_subparsers()

    # -> install -> master
    parser_install_master = parser_install_sub.add_parser("master")
    host_args(parser_install_master)
    parser_install_master.set_defaults(handler=cmd_install_master)

    # -> install -> worker
    parser_install_worker = parser_install_sub.add_parser("worker")
    parser_install_worker.add_argument("master_host", help="Master node host")
    parser_install_worker.add_argument("master_port", help="Master node port")
    parser_install_worker.add_argument("token", help="Cluster token")
    host_args(parser_install_worker)
    parser_install_worker.set_defaults(handler=cmd_install_worker)

    # -> stop
    parser_stop = parser_sub.add_parser("stop")
    parser_stop.set_defaults(handler=lambda _: parser_stop.print_help())

    parser_stop_sub = parser_stop.add_subparsers()

    # -> stop -> master
    parser_stop_master = parser_stop_sub.add_parser("master")
    host_args(parser_stop_master)
    parser_stop_master.set_defaults(handler=cmd_stop_master)

    # -> stop -> worker
    parser_stop_worker = parser_stop_sub.add_parser("worker")
    host_args(parser_stop_worker)
    parser_stop_worker.set_defaults(handler=cmd_stop_worker)

    args = parser.parse_args()
    args.handler(args)

    # if args.help and args.action is None:
    #     parser.print_help()
    #     exit(1)

    # if args.action in actions:
    #     actions[args.action](unknown)
    # else:
    #     print("No such action")
    #     print_action()
    #     exit(1)

    # master = Master(conn)
    # master.info()

    # worker = Worker(conn, "127.0.0.1", "1470", master.token)
    # worker.setup()
