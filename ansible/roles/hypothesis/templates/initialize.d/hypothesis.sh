#!/bin/bash
set -e

sudo -u liquid bash <<EOF
createdb hypothesis
psql hypothesis -c 'create extension if not exists "uuid-ossp";'

cd /opt/hypothesis/h
source ../venv/bin/activate
export DATABASE_URL="postgresql:///hypothesis"
export APP_URL="http://hypothesis.{{ liquid_domain }}"
bin/hypothesis init
EOF
