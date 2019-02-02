source scripts/const.sh

log() {
    echo "==>" "$@" 1>&2
}

error() {
    echo "!!!" "$@" 1>&2
}

warn() {
    echo "***" "$@" 1>&2
}

install-docker() {
    if ! [ -x "$(command -v docker)" ]; then
        log "installing docker"
        wget -O - https://get.docker.com/ | sh
    
        log "restarting docker with local port binding"

        mkdir -p /etc/systemd/system/docker.service.d/

        # add -H tcp://$DOCKER_HOST:$DOCKER_PORT flag
        {
            echo "[Service]"
            echo "ExecStart="
            echo "ExecStart=/usr/bin/env dockerd -H fd:// -H tcp://$DOCKER_HOST:$DOCKER_PORT"
        } > cat > /etc/systemd/system/docker.service.d/override.conf

        systemctl daemon-reload
        systemctl restart docker

        log "docker installed"
    else
        log "docker has already been installed"
    fi
}

# check if tcp port is open on $1:$2
check-tcp() {
    nc -z $1 $2
}

# get globally stored token
get-token() {
    mkdir -p /var/lib/broadway
    touch /var/lib/broadway/token
    cat /var/lib/broadway/token
}

set-token() {
    mkdir -p /var/lib/broadway
    cat > /var/lib/broadway/token
}

# $1 = container-name/id
is-container-running() {
    [ "$(docker inspect -f {{.State.Running}} $1 2>/dev/null)" == "true" ]
}

silent() {
    "$@" 1>/dev/null 2>/dev/null
}

rm-name() {
    if [ "$(docker ps -aq -f status=exited -f name=$1)" ]; then
        docker rm $1
    fi
}
