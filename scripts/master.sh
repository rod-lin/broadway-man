#! /bin/bash

set -e

source scripts/common.sh
source scripts/const.sh

install-docker

if is-container-running $CONTAINER_MONGO; then
    log "mongo container is already running"
else
    log "running mongo container"

    silent rm-name $CONTAINER_MONGO
    
    mkdir -p $MONGO_DBPATH

    docker run \
    --net=host \
    --name $CONTAINER_MONGO \
    -v $MONGO_DBPATH:/data/db \
    -d mongo:4.1-xenial \
    mongod --bind_ip=$MONGO_HOST --port=$MONGO_PORT
fi

if is-container-running $CONTAINER_MASTER; then
    log "master container is already running"
else
    if ! [ -z "$1" ]; then
        log "override cluster token $1"
        MASTER_ARGS="-e CLUSTER_TOKEN=$1"
        echo $1 | set-token
    elif ! [ -z "$(get-token)" ]; then
        TOKEN=$(get-token)
        log "using old token $TOKEN"
        MASTER_ARGS="-e CLUSTER_TOKEN=$TOKEN"
    else
        warn "no token is given"
    fi

    log "running master container"

    silent rm-name $CONTAINER_MASTER

    log "pulling master container"

    docker pull $REPO_BROADWAY_API

    docker run \
    --net=host \
    --name $CONTAINER_MASTER $MASTER_ARGS \
    -d $REPO_BROADWAY_API \
    api --db-uri=mongodb://$MONGO_HOST:$MONGO_PORT # for test --course-config=utils/config.json

    docker logs $CONTAINER_MASTER
fi
