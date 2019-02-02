#! /bin/bash

set -e

source scripts/common.sh
source scripts/const.sh

if is-container-running $CONTAINER_MASTER; then
    log "stopping $CONTAINER_MASTER"
    docker stop $CONTAINER_MASTER
fi

if is-container-running $CONTAINER_MONGO; then
    log "stopping $CONTAINER_MONGO"
    docker stop $CONTAINER_MONGO
fi
