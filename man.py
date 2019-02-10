import getpass
import logging
import argparse

from nodes import *
from testnet import *
from fabric import Connection

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

def cmd_deploy_master(args):
    for host in args.host:
        conn = make_conn(host, args)
        master = Master(conn)
        master.deploy()

def cmd_deploy_worker(args):
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

def cmd_deploy_cluster(args):
    with open(args.cluster_conf, "rb") as fp:
        cluster = Cluster.from_json(fp.read())

    host, port, token = cluster.deploy()

    logging.info("Cluster on {}:{} is deployed".format(host, port))
    logging.info("Cluster token: " + token)

def cmd_deploy_testnet(args):
    testnet = Testnet(args.name)

    host, port, token = testnet.deploy(args.subnet)
    testnet.add_worker()
    testnet.add_worker()

    logging.info("Testnet on {}:{} is deployed".format(host, port))
    logging.info("Testnet token: " + token)

def cmd_stop_testnet(args):
    testnet = Testnet(args.name)
    testnet.stop()
    logging.info("Testnet {} stopped".format(args.name))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Manage Broadway nodes")
    parser.set_defaults(handler=lambda _: parser.print_help())

    parser_sub = parser.add_subparsers()

    # -> deploy
    parser_deploy = parser_sub.add_parser("deploy", description="Deploy master/worker node")
    parser_deploy.set_defaults(handler=lambda _: parser_deploy.print_help())

    parser_deploy_sub = parser_deploy.add_subparsers()

    # -> deploy -> master
    parser_deploy_master = parser_deploy_sub.add_parser("master", description="Deploy master node")
    host_args(parser_deploy_master)
    parser_deploy_master.set_defaults(handler=cmd_deploy_master)

    # -> deploy -> worker
    parser_deploy_worker = parser_deploy_sub.add_parser("worker", description="Deploy worker node")
    parser_deploy_worker.add_argument("master_host", help="Master node host")
    parser_deploy_worker.add_argument("master_port", help="Master node port")
    parser_deploy_worker.add_argument("token", help="Cluster token")
    host_args(parser_deploy_worker)
    parser_deploy_worker.set_defaults(handler=cmd_deploy_worker)

    # -> deploy -> cluster
    parser_deploy_cluster = parser_deploy_sub.add_parser("cluster", description="Deploy a cluster")
    parser_deploy_cluster.add_argument("cluster_conf", help="JSON configuration for the cluster")
    parser_deploy_cluster.set_defaults(handler=cmd_deploy_cluster)

    # -> deploy -> testnet
    parser_deploy_testnet = parser_deploy_sub.add_parser("testnet", description="Deploy a cluster locally using docker")
    parser_deploy_testnet.add_argument("name", help="Identifier of the testnet")
    parser_deploy_testnet.add_argument("subnet", help="Subnet to deploy the cluster")
    parser_deploy_testnet.set_defaults(handler=cmd_deploy_testnet)

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

    # -> stop -> testnet
    parser_stop_testnet = parser_stop_sub.add_parser("testnet", description="Stop a testnet")
    parser_stop_testnet.add_argument("name", help="Identifier of the testnet")
    parser_stop_testnet.set_defaults(handler=cmd_stop_testnet)

    # -> mongo
    parser_mongo = parser_sub.add_parser("mongo", description="Manage MongoDB on a master node")
    host_args(parser_mongo, single=True)
    parser_mongo.set_defaults(handler=cmd_mongo)

    # -> token
    parser_token = parser_sub.add_parser("token", description="Get master node token")
    host_args(parser_token, single=True)
    parser_token.set_defaults(handler=cmd_token)

    args = parser.parse_args()
    args.handler(args)
