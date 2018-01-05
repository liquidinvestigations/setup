#!/bin/bash

set -e
set -x

cd /opt/liquid-core

USERS=/var/lib/liquid/core/users.json

# create initial users from list, if it exists
if [ -f $USERS ]; then
  sudo -u liquid-apps venv/bin/python liquid-core/manage.py createusers $USERS
  rm $USERS
fi
