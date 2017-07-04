#!/bin/bash
set -e
set -x

cd /opt/hypothesis

if [ ! -e libexec/secrets.sh ]; then
  echo "export SECRET_KEY='$(openssl rand -base64 32 | tr -d '\n')'" >> libexec/secrets.sh
  echo "export CLIENT_ID='$(openssl rand -base64 32 | tr -d '\n')'" >> libexec/secrets.sh
  echo "export CLIENT_SECRET='$(openssl rand -base64 32 | tr -d '\n')'" >> libexec/secrets.sh
fi

supervisorctl start hypothesis-elasticsearch

sudo -u liquid bash <<EOF
set -x
createdb hypothesis
psql hypothesis -c 'create extension if not exists "uuid-ossp";'

source venv/bin/activate
cd h
export DATABASE_URL="postgresql:///hypothesis"
export APP_URL="http://hypothesis.{{ liquid_domain }}"
export ELASTICSEARCH_HOST="http://127.0.0.1:14312"
bin/hypothesis init
EOF

# Start remaining services now, and autostart on subsequent boots
supervisorctl start hypothesis-beat hypothesis-web hypothesis-websocket hypothesis-worker
sed -i '/autostart = false/d' /etc/supervisor/conf.d/hypothesis.conf
