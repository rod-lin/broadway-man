from fabric import Connection

import getpass
import argparse

from nodes import *

def make_conn(host, pubkey=False, password=None):
    if not pubkey and password is None:
        password = getpass.getpass("Password for connection to {}: ".format(host))

    return Connection(host, connect_kwargs={ "password": password })

actions = {}

def action(name):
    """action decorator"""
    def decorator(f):
        actions[name] = f
        return f

    return decorator

def print_action():
    print("Available action:", *[ a for a in actions ])

def host_args(parser):
    parser.add_argument("host", nargs="*", help="[user@]<host>")
    parser.add_argument("--use-pubkey", action="store_const", const=True,
                        help="Use public key instead of asking for password")

@action("stop")
def action_stop(argv):
    """stop nodes"""

    parser = argparse.ArgumentParser(description="Stop nodes")
    parser.add_argument("node_role", help="Role of the node(master, worker, etc.)")
    host_args(parser)

    args = parser.parse_args(argv)

    if not len(args.host):
        print("No host given")

    for host in args.host:
        conn = make_conn(host, pubkey=args.use_pubkey)

        if args.node_role == "master":
            master = Master(conn)
            master.stop()
        elif args.node_role == "worker":
            worker = Worker(conn)
            worker.stop()
        else:
            print("Unknown node role: " + args.node_role)
            parser.print_help()

@action("install")
def action_install(argv):
    """install broadway to nodes"""

    parser = argparse.ArgumentParser(description="Install nodes")
    parser.add_argument("node_role", help="Role of the node(master, worker, etc.)")
    host_args(parser)

    parser.add_argument("--token", help="Cluster token")
    parser.add_argument("--master", help="Address of master node(e.g. 127.0.0.1:1470)")

    args = parser.parse_args(argv)

    if not len(args.host):
        print("No host given")

    for host in args.host:
        conn = make_conn(host, pubkey=args.use_pubkey)

        if args.node_role == "master":
            master = Master(conn)
            master.setup()
        elif args.node_role == "worker":
            if args.token is None or args.master is None:
                print("worker requires a token and a master node")
                return

            master = args.master.split(":")
            if len(master) != 2:
                print("Wrong master address format {}".format(args.master))
                return

            worker = Worker(conn)
            worker.setup(master[0], master[1], args.token)
        else:
            print("Unknown node role: " + args.node_role)
            parser.print_help()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Broadway nodes")
    parser.add_argument("action", help="Action")

    args, unknown = parser.parse_known_args()

    if args.action in actions:
        actions[args.action](unknown)
    else:
        print("No such action")
        print_action()
        exit(1)

    # master = Master(conn)
    # master.info()

    # worker = Worker(conn, "127.0.0.1", "1470", master.token)
    # worker.setup()
