#! /bin/bash

set -e

source scripts/common.sh
source scripts/const.sh

if is-container-running $CONTAINER_WORKER; then
    log "stopping $CONTAINER_WORKER"
    docker stop $CONTAINER_WORKER
fi
