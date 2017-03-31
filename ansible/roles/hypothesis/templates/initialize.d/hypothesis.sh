#!/bin/bash
set -e

sudo -u liquid bash <<EOF
createdb hypothesis
psql hypothesis -c 'create extension if not exists "uuid-ossp";'

cd /opt/hypothesis/h
source ../venv/bin/activate
export DATABASE_URL="postgresql:///hypothesis"
export APP_URL="http://hypothesis.{{ liquid_domain }}"
export ELASTICSEARCH_HOST="http://127.0.0.1:14312"
bin/hypothesis init
EOF
