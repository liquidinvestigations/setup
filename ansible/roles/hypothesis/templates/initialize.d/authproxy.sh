#!/bin/bash -ex

sudo -u liquid-apps /opt/liquid-core/libexec/create-oauth-application "hypothesis" "{{ http_scheme }}://hypothesis.{{ liquid_domain }}/__auth/callback"

echo "Creating secret keys..."
set +x
source /var/lib/liquid/oauth_keys/hypothesis
echo "LIQUID_CLIENT_ID = '$CLIENT_ID'" > /opt/hypothesis/authproxy/config/oauth.py
echo "LIQUID_CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/hypothesis/authproxy/config/oauth.py

if [ ! -s /opt/hypothesis/authproxy/config/secret.py ]; then
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/hypothesis/authproxy/config/secret.py
fi

set -x

supervisorctl start hypothesis-authproxy
