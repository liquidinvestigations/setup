#!/bin/bash

set -e
source /var/lib/liquid/oauth_keys/davros
echo "LIQUID_CLIENT_ID = '$CLIENT_ID'" > /opt/davros/authproxy/config/oauth.py
echo "LIQUID_CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/davros/authproxy/config/oauth.py
