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

# if the davros-sync collection exists, exit
if [ -f /var/lib/liquid/hoover/created-davros-sync ]; then exit 0; fi

# create the davros-sync collection
supervisorctl start hoover-tika
supervisorctl start hoover-snoop2

# create the davros-sync collection and walk / digest it
sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover snoop2 createcollection davros-sync '$DAVROS_DATA_PATH'
/opt/hoover/bin/hoover snoop2 rundispatcher
touch /var/lib/liquid/hoover/created-davros-sync
EOF

# wait after hoover's tika
tika_url="http://localhost:15423"
wait_url $tika_url

supervisorctl stop hoover-tika
supervisorctl start hoover-elasticsearch

# wait after hoover's elasticsearch
es_url="http://localhost:14352"
wait_url $es_url

sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover search addcollection davros-sync "$snoop_url/collections/davros-sync/json" --public
/opt/hoover/bin/hoover search resetindex davros-sync
EOF

snoop_url="http://localhost:11941"
wait_url $snoop_url/collections/davros-sync/json


sudo -u liquid-apps bash <<EOF
set -x
/opt/hoover/bin/hoover search update davros-sync
EOF

# DON'T MAKE THIS COLLECTION PUBLIC
#sudo -u liquid-apps /opt/hoover/bin/hoover search shell <<EOF
#from hoover.search.models import Collection
#c = Collection.objects.get(name='davros-sync')
#c.public = True
#c.save()
#EOF

supervisorctl stop hoover-snoop2
supervisorctl stop hoover-elasticsearch

sudo -u liquid-apps bash <<EOF
set -x
. /opt/hoover/venvs/snoop2/bin/activate
cd /opt/hoover/snoop2
#py.test
EOF
