FROM docker:dind

RUN apk update && \
    apk add bash git openssh rsync augeas sudo && \
    rm /bin/sh && \
    ln -s /bin/bash /bin/sh && \
    rm -rf /var/cache/apk/*

RUN echo root:docker | chpasswd && \
    mkdir -p /etc/ssh/keys && \
    ssh-keygen -A && \
    mv /etc/ssh/ssh_host_* /etc/ssh/keys/ && \
    printf '%s\n' \
        'set /files/etc/ssh/sshd_config/HostKey[1] /etc/ssh/keys/ssh_host_rsa_key' \
        'set /files/etc/ssh/sshd_config/HostKey[2] /etc/ssh/keys/ssh_host_dsa_key' \
        'set /files/etc/ssh/sshd_config/HostKey[3] /etc/ssh/keys/ssh_host_ecdsa_key' \
        'set /files/etc/ssh/sshd_config/HostKey[4] /etc/ssh/keys/ssh_host_ed25519_key' \
        'set /files/etc/ssh/sshd_config/PasswordAuthentication yes' \
        'set /files/etc/ssh/sshd_config/PermitRootLogin yes' \
        'set /files/etc/ssh/sshd_config/Port 22' \
    | augtool -s

CMD [ "/usr/sbin/sshd", "-D", "-f", "/etc/ssh/sshd_config" ]
