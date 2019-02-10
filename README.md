# Broadway Manager

`broadway.man` is a module for managing broadway nodes.

### Installation

    pip install git+https://github.com/rod-lin/broadway-man

### Node types

- Master node: docker, broadway-api, and mongodb
- Worker node: docker, broadway-grader

### Command line usage

Print help message

    python -m broadway.man -h

Deploy nodes

    # deploy a master node on user@host
    python -m broadway.man deploy master user@host
    
    # deploy a worker node on user@host
    python -m broadway.man deploy worker \
        <master host> <master port> <cluster token> user@host
        
    # deploy a cluster with cluster configuration
    # cluster config format:
    # {
    #     "master": { "host": "user@host" },
    #     "worker": [ { "host": "user@host" }, { "host": "user@host" }, ... ]
    # }
    python -m broadway.man deploy cluster cluster.json
    
    # deploy a testnet on locally
    python -m broadway.man deploy testnet <testnet name> <subnet> <number of worker nodes>
    
    # e.g. to deploy a testnet with one master node at 10.2.0.1 and three worker nodes
    python -m broadway.man deploy testnet testnet-1 10.2.0.0/24 3

Stop nodes

    # stop a master/worker node
    python -m broadway.man stop master user@host
    python -m broadway.man stop worker user@host
    
    # stop a testnet
    python -m broadway.man stop testnet <testnet name>
    
Get master node token

    python -m broadway.man token user@host
    
    # e.g. to get token of a testnet(default password is empty for a testnet)
    python -m broadway.man token root@<testnet addr>    
