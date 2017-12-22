#!/bin/bash

set -ex

echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/discover/discover/settings/secret_key.py

supervisorctl start liquid-discover
supervisorctl start avahi-daemon
