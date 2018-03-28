#!/bin/bash
set -e
set -x

cd /opt/hypothesis

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

SECRETS_PATH=/var/lib/liquid/data/hypothesis/secrets.sh
if [ ! -e $SECRETS_PATH ]; then
  set +x
  echo "Creating secret keys..."
  echo "export SECRET_KEY='$(openssl rand -base64 32 | tr -d '\n')'" > $SECRETS_PATH
  echo "export CLIENT_ID='$(openssl rand -base64 32 | tr -d '\n')'" >> $SECRETS_PATH
  echo "export CLIENT_SECRET='$(openssl rand -base64 32 | tr -d '\n')'" >> $SECRETS_PATH
  set -x
fi

supervisorctl start hypothesis-elasticsearch
# Wait for hypothesis-elasticsearch because hypothesis init must be able to connect
wait_url 'http://127.0.0.1:14312'

sudo -u liquid-apps bash <<EOF
set -x
createdb hypothesis
psql hypothesis -c 'create extension if not exists "uuid-ossp";'

source venv/bin/activate
cd h
export DATABASE_URL="postgresql:///hypothesis"
export APP_URL="http://hypothesis.{{ liquid_domain }}"
export ELASTICSEARCH_HOST="http://127.0.0.1:14312"
export SECRET_KEY="temporary secret key for initialize"
export AUTH_DOMAIN="hypothesis.{{ liquid_domain }}"
bin/hypothesis init
EOF

# Start remaining services
supervisorctl start hypothesis-beat hypothesis-web hypothesis-websocket hypothesis-worker
