from fabric import Connection

import getpass
import argparse

from nodes import *

def make_conn(host, args):
    password = None

    if args.password is not None:
        password = args.password

    if not args.use_pubkey and password is None:
        password = getpass.getpass("Password for connection to {}: ".format(host))

    return Connection(host, connect_kwargs={ "password": password })

def host_args(parser, single=False):
    parser.add_argument("host", nargs=None if single else "+", help="[user@]<host>")
    parser.add_argument("--use-pubkey", action="store_const", const=True,
                        help="Use public key instead of asking for password")
    parser.add_argument("--password", help="Use the given password. This will apply to all given hosts")

def cmd_install_master(args):
    for host in args.host:
        conn = make_conn(host, args)
        master = Master(conn)
        master.deploy()

def cmd_install_worker(args):
    for host in args.host:
        conn = make_conn(host, args)
        worker = Worker(conn)
        worker.deploy(args.master_host, args.master_port, args.token)

def cmd_stop_master(args):
    for host in args.host:
        conn = make_conn(host, args)
        master = Master(conn)
        master.stop()

def cmd_stop_worker(args):
    for host in args.host:
        conn = make_conn(host, args)
        worker = Worker(conn)
        worker.stop()

def cmd_mongo(args):
    conn = make_conn(args.host, args)
    master = Master(conn)
    master.sudo("docker exec -it {} mongo --host {} --port {}" \
                .format(SCRIPT_CONST["CONTAINER_MONGO"], SCRIPT_CONST["MONGO_HOST"], SCRIPT_CONST["MONGO_PORT"]))

def cmd_token(args):
    conn = make_conn(args.host, args)
    master = Master(conn)
    master.get_token()

def cmd_cluster(args):
    with open(args.cluster_conf, "rb") as fp:
        cluster = Cluster.from_json(fp.read())

    host, port, token = cluster.deploy()

    print("Cluster on {}:{} is deployed".format(host, port))
    print("Cluster token: " + token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Broadway nodes")
    parser.set_defaults(handler=lambda _: parser.print_help())

    parser_sub = parser.add_subparsers()

    # -> install
    parser_install = parser_sub.add_parser("install", description="Install master/worker node")
    parser_install.set_defaults(handler=lambda _: parser_install.print_help())

    parser_install_sub = parser_install.add_subparsers()

    # -> install -> master
    parser_install_master = parser_install_sub.add_parser("master", description="Install master node")
    host_args(parser_install_master)
    parser_install_master.set_defaults(handler=cmd_install_master)

    # -> install -> worker
    parser_install_worker = parser_install_sub.add_parser("worker", description="Install worker node")
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
    parser_stop_master = parser_stop_sub.add_parser("master", description="Stop master node")
    host_args(parser_stop_master)
    parser_stop_master.set_defaults(handler=cmd_stop_master)

    # -> stop -> worker
    parser_stop_worker = parser_stop_sub.add_parser("worker", description="Stop worker node")
    host_args(parser_stop_worker)
    parser_stop_worker.set_defaults(handler=cmd_stop_worker)

    # -> mongo
    parser_mongo = parser_sub.add_parser("mongo", description="Manage MongoDB on a master node")
    host_args(parser_mongo, single=True)
    parser_mongo.set_defaults(handler=cmd_mongo)

    # -> token
    parser_token = parser_sub.add_parser("token", description="Get master node token")
    host_args(parser_token, single=True)
    parser_token.set_defaults(handler=cmd_token)

    # -> cluster
    parser_cluster = parser_sub.add_parser("cluster", description="Deploy a cluster")
    parser_cluster.add_argument("cluster_conf", help="JSON configuration for the cluster")
    parser_cluster.set_defaults(handler=cmd_cluster)

    args = parser.parse_args()
    args.handler(args)
