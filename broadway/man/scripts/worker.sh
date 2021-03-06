#! /bin/bash

set -e

source scripts/common.sh
source scripts/const.sh

help() {
    echo "usage: $0 <master host> <master port> <cluster token>"
}

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    help
    exit 1
fi

MASTER_HOST=$1
MASTER_PORT=$2
CLUSTER_TOKEN=$3

log "checking connectivity"

if ! check-tcp $MASTER_HOST $MASTER_PORT; then
    error "failed to connect to master node"
    exit 1
fi

install-docker

# disable apparmor
if has-command systemctl; then
    log "disabling app armor"
    systemctl stop apparmor && systemctl disable apparmor
else
    log "systemd not found, leaving app armor open"
fi

if is-container-running $CONTAINER_WORKER; then
    log "worker container is already running"
else
    log "running worker container"

    silent rm-container-name $CONTAINER_WORKER

    log "pulling worker container"

    docker pull $REPO_BROADWAY_GRADER

    log "creating work dir $GRADER_WORKDIR"

    mkdir -p $GRADER_WORKDIR

    docker run \
    --net=host \
    --name $CONTAINER_WORKER \
    -v $GRADER_WORKDIR:$GRADER_WORKDIR \
    -e DOCKER_HOST=tcp://$DOCKER_HOST:$DOCKER_PORT \
    -d $REPO_BROADWAY_GRADER \
    grader $MASTER_HOST $MASTER_PORT $CLUSTER_TOKEN --workdir=$GRADER_WORKDIR
fi
