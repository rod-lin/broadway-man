#! /bin/bash

set -e

source scripts/common.sh
source scripts/const.sh

if is-container-running $CONTAINER_WORKER; then
    log "stopping $CONTAINER_WORKER"

    if stop-container $CONTAINER_WORKER; then
        log "stopped $CONTAINER_WORKER"
    else
        error "failed to stop $CONTAINER_WORKER"
    fi
else
    log "$CONTAINER_WORKER is not running"
fi
