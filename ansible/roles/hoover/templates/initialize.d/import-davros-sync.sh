#!/bin/bash
set -e
set -x

cd /opt/hoover

function wait_url {
    X=0
    until $(curl --connect-timeout 3 --max-time 20 --output /dev/null --silent --head --fail $1); do
        sleep 3
        ((X=X+1))
        if [[ $X -gt 20 ]]; then
            echo "wait_url: $1 timed out" >&2
            exit 1;
        fi
    done
}

supervisorctl start hoover-elasticsearch

DAVROS_DATA_PATH=/var/lib/liquid/data/davros-sync

# create the davros-sync collection
if [ -f /var/lib/liquid/hoover/created-davros-sync ]; then exit 0; fi

supervisorctl start hoover-elasticsearch

# wait after hoover's elasticsearch
es_url="http://localhost:14352"
wait_url $es_url

# create the davros-sync collection and walk / digest it
sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover snoop2 createcollection davros-sync '$DAVROS_DATA_PATH'
/opt/hoover/bin/hoover snoop2 resetcollectionindex davros-sync
/opt/hoover/bin/hoover snoop2 rundispatcher
/opt/hoover/bin/hoover search addcollection davros-sync "$snoop_url/collections/davros-sync/json" --public
touch /var/lib/liquid/hoover/created-davros-sync
EOF
