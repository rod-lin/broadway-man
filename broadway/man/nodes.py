import os
import uuid
import json
import string
import invoke
import getpass
import tempfile

from .utils import *
from .const import *
from jsonschema import validate
from fabric import Connection

def filter_visible(s):
    return "".join(filter(lambda x: x in string.printable and x not in string.whitespace, s))

class Node:
    """base class for a node"""

    def __init__(self, conn):
        self.conn = conn

        password = conn.connect_kwargs.get("password")

        cwd = prog_dir()

        self.password = \
            password if password is not None else \
            getpass.getpass("sudo password for {}@{}: ".format(conn.user, conn.host))

        self.sudo("mkdir -p {}/scripts".format(BASE_DIR))
        self.sudo("chown -R {} {}".format(self.conn.user, BASE_DIR))

        # upload all scripts
        for file in os.listdir("{}/scripts".format(cwd)):
            if file.endswith(".sh"):
                self.conn.put("{}/scripts/{}".format(cwd, file), "{}/scripts".format(BASE_DIR))

        # generate const.sh
        _, path = tempfile.mkstemp()

        with open(path, "wb") as f:
            f.write(Node.gen_const_sh().encode("utf-8"))

        self.conn.put(path, "{}/scripts/const.sh".format(BASE_DIR))
        os.unlink(path)

    @staticmethod
    def gen_const_sh():
        """generate scripts/const.sh"""
        lines = []
        
        for key in SCRIPT_CONST:
            lines.append("{}=\"{}\"".format(key, SCRIPT_CONST[key]))

        return "\n".join(lines)

    def info(self):
        self.conn.run("uname -a")

    # run in BASE_DIR
    def run(self, cmd):
        try:
            res = self.conn.run("if [ -d {} ]; then cd {}; fi && bash -c '{}'" \
                                .format(BASE_DIR, BASE_DIR, cmd), pty=True)
        except invoke.exceptions.UnexpectedExit as exc:
            res = exc.result

        if res.return_code:
            raise Exception("Command `{}` exited with code {}".format(cmd, res.return_code))

        return res

    def sudo(self, orig_cmd):
        # set sudo prompt to an invisible character to avoid default prompt
        cmd = "if [ -d {} ]; then cd {}; fi && echo '{}' | sudo -S -p $(echo -ne '\x07') {}" \
              .format(BASE_DIR, BASE_DIR, self.password, orig_cmd)
        
        try:
            res = self.conn.run(cmd, pty=True)
        except invoke.exceptions.UnexpectedExit as exc:
            res = exc.result

        if res.return_code:
            raise Exception("Command `{}` exited with code {}".format(orig_cmd, res.return_code))

        return res

class Master(Node):
    def __init__(self, conn, token=str(uuid.uuid4())):
        super().__init__(conn)
        self.token = token

    def deploy(self):
        return self.sudo("bash scripts/master.sh {}".format(self.token))

    def stop(self):
        return self.sudo("bash scripts/stop-master.sh")

    def get_token(self):
        res = self.sudo("bash scripts/token.sh")
        token = filter_visible(res.stdout)

        return token if len(token) else None

    def get_address(self):
        return self.conn.host, SCRIPT_CONST["MASTER_PORT"]

class Worker(Node):
    def __init__(self, conn):
        super().__init__(conn)

    def deploy(self, host, port, token):
        return self.sudo("bash scripts/worker.sh {} {} {}".format(host, port, token))

    def stop(self):
        return self.sudo("bash scripts/stop-worker.sh")

class Cluster:
    @staticmethod
    def make_conn(node_conf, role="node"):
        host = node_conf["host"]
        password = getpass.getpass("Password for connection to {} {}: ".format(role, host))

        return Connection(host, connect_kwargs={ "password": password })

    @staticmethod
    def from_json(json_str):
        conf = json.loads(json_str)
        validate(conf, CLUSTER_CONF_DEF)

        master_conn = Cluster.make_conn(conf["master"], role="master node")
        master_node = Master(master_conn)

        worker_nodes = []

        for worker in conf["workers"]:
            worker_conn = Cluster.make_conn(worker, role="worker node")
            worker_node = Worker(worker_conn)
            worker_nodes.append(worker_node)

        return Cluster(master_node, worker_nodes)

    def __init__(self, master, workers):
        self.master = master
        self.workers = workers

    def deploy(self):
        self.master.deploy()
        token = self.master.get_token()

        if token is None:
            raise Exception("Incorrect deployment. Couldn't get cluster token")

        host, port = self.master.get_address()

        for worker in self.workers:
            worker.deploy(host, port, token)

        return host, port, token
