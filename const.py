BASE_DIR = "/broadway"

# will be used to generate const.sh
SCRIPT_CONST = {
    # for master
    "MONGO_HOST": "127.0.0.1",
    "MONGO_PORT": "3142",
    "MONGO_DBPATH": "/data/db",

    "MASTER_PORT": "3143",

    # for worker
    "DOCKER_HOST": "127.0.0.1",
    "DOCKER_PORT": "3141",
    "GRADER_WORKDIR": "/data/job",

    "CONTAINER_MASTER": "broadway-master",
    "CONTAINER_MONGO": "broadway-mongo",
    "CONTAINER_WORKER": "broadway-worker",

    "REPO_BROADWAY_API": "illinois241/broadway-api",
    "REPO_BROADWAY_GRADER": "illinois241/broadway-grader"
}

NODE_CONF_DEF = {
    "type": "object",
    "properties": {
        "host": { "type": "string" }
    },

    "required": [ "host" ],
    "additionalProperties": False
}

CLUSTER_CONF_DEF = {
    "type": "object",
    "properties": {
        "master": NODE_CONF_DEF,
        "workers": {
            "type": "array",
            "items": NODE_CONF_DEF
        }
    },

    "required": [ "master", "workers" ],
    "additionalProperties": False
}
