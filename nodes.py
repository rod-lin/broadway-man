import os
import uuid
import getpass

from const import *

class Node:
    """base class for a node"""

    def __init__(self, conn):
        self.conn = conn

        password = conn.connect_kwargs.get("password")

        self.password = \
            password if password is not None else \
            getpass.getpass("sudo password for {}@{}: ".format(conn.user, conn.host))

        self.sudo("mkdir -p {}/scripts".format(BASE_DIR))
        self.sudo("chown -R {} {}".format(self.conn.user, BASE_DIR))

        # upload all scripts
        for file in os.listdir("scripts"):
            if file.endswith(".sh"):
                self.conn.put("scripts/{}".format(file), "{}/scripts".format(BASE_DIR))

    def info(self):
        self.conn.run("uname -a")

    # run in BASE_DIR
    def run(self, cmd):
        return self.conn.run("cd {} && bash -c '{}'".format(BASE_DIR, cmd))

    def sudo(self, cmd):
        # set sudo prompt to an invisible character to avoid default prompt
        cmd = "cd {} && echo '{}' | sudo -S -p $(echo -ne '\x07') {}".format(BASE_DIR, self.password, cmd)
        return self.conn.run(cmd, pty=True)

class Master(Node):
    def __init__(self, conn, token=str(uuid.uuid4())):
        super().__init__(conn)
        self.token = token

    def setup(self):
        self.sudo("bash scripts/master.sh {}".format(self.token))

    def stop(self):
        self.sudo("bash scripts/stop-master.sh")

class Worker(Node):
    def __init__(self, conn):
        super().__init__(conn)

    def setup(self, host, port, token):
        self.sudo("bash scripts/worker.sh {} {} {}".format(host, port, token))

    def stop(self):
        self.sudo("bash scripts/stop-worker.sh")
