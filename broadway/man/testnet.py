import re
import docker
import logging

from .nodes import *
from .utils import prog_dir
from fabric import Connection

RE_SUBNET = r"((\d+.\d+.\d+).\d+)/(\d+)"
NESTED_USER = "root"
NESTED_PASSWORD = "docker" # set in Dockerfile

NETWORK_PREFIX = "broadway-testnet"
CONTAINER_PREFIX = "broadway-testnet"

MAX_WORKER = 128

class Testnet:
    def __init__(self, name, network_prefix=NETWORK_PREFIX):
        self.client = docker.from_env()
        self.node_count = 0
        self.network = network_prefix + "-" + name
        self.name = name

        self.subnet = None
        self.ip_netbits = None

        self.master = None
        self.workers = []

    # stop all containers with name  CONTAINER_PREFIX + "-" + self.name + "-" + n
    def stop(self):
        prefix = CONTAINER_PREFIX + "-" + self.name + "-"
        containers = self.client.containers.list()

        for container in containers:
            if (container.name or "").startswith(prefix):
                logging.info("Stopping node {}".format(container.name))
                container.stop()

        # remove network
        logging.info("Removing network {}".format(self.network))
        network = self.client.networks.get(self.network)
        network.remove()

    def deploy(self, subnet):
        match = re.match(RE_SUBNET, subnet)

        if match is None:
            raise Exception("Wrong subnet format " + subnet)

        if int(match.group(3)) < 8:
            raise Exception("Too little subnet range " + match.group(3))

        self.subnet = subnet
        self.ip_netbits = match.group(2)

        ipam_pool = docker.types.IPAMPool(subnet=self.subnet)
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        # remove existing network
        try:
            nets = self.client.networks.list(names=[ self.network ])
            for net in nets:
                net.remove()
        except: pass
        
        self.client.networks.create(self.network, driver="bridge", ipam=ipam_config)
        
        # build image for broadway node
        self.client.images.build(path="{}/nested".format(prog_dir()), tag="broadway-nested")

        # setup master
        conn = self.deploy_node()
        self.master = Master(conn)
        self.master.deploy()

        host, port = self.master.get_address()

        return host, port, self.master.get_token()

    def get_node_ip(self, node_n):
        return self.ip_netbits + "." + str(node_n)

    def get_node_name(self, node_n):
        return CONTAINER_PREFIX + "-" + self.name + "-" + str(node_n)

    def deploy_node(self):
        self.node_count += 1

        if self.node_count > MAX_WORKER:
            raise Exception("Too many workers")

        ip = self.get_node_ip(self.node_count)
        name = self.get_node_name(self.node_count)

        logging.info("Deploying node {} at {}".format(name, ip))

        try:
            container = self.client.containers.get(name)
            if container.status == "running":
                raise Exception("container of the same name `{}` is still running".format(name))
            
            container.remove() # remove name
        except:
            pass

        # start a node in the network
        server = self.client.containers.create("broadway-nested", name=name, detach=True, privileged=True)
        self.client.networks.get(self.network).connect(server, ipv4_address=ip)
        server.start()

        conn = Connection(NESTED_USER + "@" + ip, connect_kwargs={ "password": NESTED_PASSWORD })

        while True:
            logging.info("Trying to connect to {}".format(ip))
            try: conn.open(); break
            except: pass

        return conn

    # deploy one worker
    def add_worker(self):
        conn = self.deploy_node()
        worker = Worker(conn)

        host, port = self.master.get_address()

        worker.deploy(host, port, self.master.get_token())
