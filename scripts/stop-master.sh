#! /bin/bash

set -e

source scripts/common.sh
source scripts/const.sh

if is-container-running $CONTAINER_MASTER; then
    log "stopping $CONTAINER_MASTER"

    if stop-container $CONTAINER_MASTER; then
        log "stopped $CONTAINER_MASTER"
    else
        error "failed to stop $CONTAINER_MASTER"
    fi
else
    log "$CONTAINER_MASTER is not running"
fi

if is-container-running $CONTAINER_MONGO; then
    log "stopping $CONTAINER_MONGO"
    
    if stop-container $CONTAINER_MONGO; then
        log "stopped $CONTAINER_MONGOR"
    else
        error "failed to stop $CONTAINER_MONGO"
    fi
else
    log "$CONTAINER_MONGO is not running"
fi
