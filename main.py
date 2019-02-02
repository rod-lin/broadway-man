from fabric import Connection

import os
import uuid
import getpass

BASE_DIR = "/broadway"

class Node:
    """base class for a node"""

    def __init__(self, conn):
        self.conn = conn
        self.password = getpass.getpass("Password for connection to {}@{}: ".format(conn.user, conn.host))

    def setup(self):
        self.conn.sudo("mkdir -p {}/scripts".format(BASE_DIR), password=self.password)
        self.conn.sudo("chown -R {} {}".format(self.conn.user, BASE_DIR), password=self.password)

        # upload all scripts
        for file in os.listdir("scripts"):
            if file.endswith(".sh"):
                self.conn.put("scripts/{}".format(file), "{}/scripts".format(BASE_DIR))

    # run in BASE_DIR
    def run(self, cmd):
        return self.conn.run("cd {} && bash -c '{}'".format(BASE_DIR, cmd))

    def sudo(self, cmd):
        return self.conn.sudo("bash -c 'cd {} && {}'".format(BASE_DIR, cmd), password=self.password)

class Master(Node):
    def __init__(self, conn, token=str(uuid.uuid4())):
        super().__init__(conn)
        self.token = token

    def setup(self):
        super().setup()
        self.sudo("bash scripts/master.sh {}".format(self.token))

    def stop(self):
        self.sudo("bash scripts/stop-master.sh")

class Worker(Node):
    def __init__(self, conn, host, port, token):
        super().__init__(conn)
        self.host = host
        self.port = port
        self.token = token

    def setup(self):
        super().setup()
        self.sudo("bash scripts/worker.sh {} {} {}".format(self.host, self.port, self.token))

    def stop(self):
        self.sudo("bash scripts/stop-worker.sh")

conn = Connection("rodlin@ric0.could.fail")

master = Master(conn)
master.setup()

worker = Worker(conn, "127.0.0.1", "1470", master.token)
worker.setup()

# node.stop()

# print(node.run("ls").stdout)
