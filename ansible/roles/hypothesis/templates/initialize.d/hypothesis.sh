#!/bin/bash
set -e

cd /opt/hypothesis

if [ ! -e libexec/secret_key.sh ]; then
  echo "export SECRET_KEY='$(openssl rand -base64 32 | tr -d '\n')'" > libexec/secret_key.sh
fi

supervisorctl start hypothesis-elasticsearch

sudo -u liquid bash <<EOF
createdb hypothesis
psql hypothesis -c 'create extension if not exists "uuid-ossp";'

source venv/bin/activate
cd h
export DATABASE_URL="postgresql:///hypothesis"
export APP_URL="http://hypothesis.{{ liquid_domain }}"
export ELASTICSEARCH_HOST="http://127.0.0.1:14312"
bin/hypothesis init
EOF

supervisorctl stop hypothesis-elasticsearch
