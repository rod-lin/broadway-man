source /etc/profile
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

silent() {
    "$@" 1>/dev/null 2>/dev/null
}

# the script depends on wget and nc
check-dep() {
    if ! has-command wget || ! has-command nc || ! has-command grep; then
        error "this script requires wget, nc, and grep"
        exit 1
    fi
}

is-systemd() {
    [ "$(stat /proc/1/exe | grep systemd)" ]
}

# check if docker if alive on $DOCKER_HOST:$DOCKER_PORT
check-docker() {
    DOCKER_HOST=$DOCKER_HOST:$DOCKER_PORT docker info 1>/dev/null 2>/dev/null
}

has-command() {
    command -v $1 1>/dev/null 2>/dev/null
}

wait-cond() {
    echo -n $1
    
    while "${@:2}"; do
        echo -n "."
        sleep 1
    done

    echo ""
}

install-docker() {
    if ! has-command docker; then
        log "installing docker"
        wget -O - https://get.docker.com/ | sh
        log "docker installed"
    else
        log "docker has already been installed"
    fi

    if ! check-docker; then
        if is-systemd; then
            log "detected systemd"
        
            log "configuring docker on $DOCKER_HOST:$DOCKER_PORT for systemd"

            mkdir -p /etc/systemd/system/docker.service.d/

            systemctl start docker # start service before cat
            CURRENT_EXECSTART="$(systemctl cat docker | grep ExecStart= | head -n 1)"

            log "current $CURRENT_EXECSTART"

            # add -H tcp://$DOCKER_HOST:$DOCKER_PORT flag
            {
                echo "[Service]"
                echo "ExecStart="
                echo "$CURRENT_EXECSTART -H tcp://$DOCKER_HOST:$DOCKER_PORT"
            } > cat > /etc/systemd/system/docker.service.d/override.conf

            systemctl daemon-reload
            systemctl restart docker

            log "docker restarted"
        else
            if [ -w /etc/default/docker ]; then
                log "systemd not detected"

                # for sysvinit or upstart
                log "configuring docker on $DOCKER_HOST:$DOCKER_PORT for sysvinit/upstart"

                echo "DOCKER_OPTS=\"-H tcp://$DOCKER_HOST:$DOCKER_PORT\"" >> /etc/default/docker
                service docker restart

                log "docker restarted"
            else
                log "unrecognized config, trying directly starting dockerd"

                if [ -f /var/run/docker.pid ]; then
                    log "killing dockerd"
                    
                    kill $(cat /var/run/docker.pid)

                    wait-cond "waiting for dockerd to stop" [ -f /var/run/docker.pid ]
                fi

                nohup dockerd -H unix:///var/run/docker.sock -H "tcp://$DOCKER_HOST:$DOCKER_PORT" &

                log "docker started"
            fi
        fi
    fi

    sleep 1

    if ! check-docker; then
        error "failed to set up docker at tcp://$DOCKER_HOST:$DOCKER_PORT"
        exit 1
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

rm-container-name() {
    if [ "$(docker ps -aq -f status=exited -f name=$1)" ]; then
        docker rm $1
    fi
}

stop-container() {
    [ "$(docker stop $1)" == $1 ]
}

check-dep
