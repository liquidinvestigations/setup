#!/bin/bash

# create initial admin user

cd /opt/liquid-core

if [ -f users.json ]; then
  sudo -u liquid venv/bin/python liquid-core/manage.py createusers users.json
  rm users.json
fi
