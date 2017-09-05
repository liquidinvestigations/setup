#!/bin/bash

set -e

sudo -u liquid /opt/liquid-core/libexec/create-oauth-application "davros" "{{ http_scheme }}://davros.{{ liquid_domain }}/__auth/callback"
source /var/lib/liquid/oauth_keys/davros
echo "LIQUID_CLIENT_ID = '$CLIENT_ID'" > /opt/davros/authproxy/config/oauth.py
echo "LIQUID_CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/davros/authproxy/config/oauth.py
