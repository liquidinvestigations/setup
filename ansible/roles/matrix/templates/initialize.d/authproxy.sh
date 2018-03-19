#!/bin/bash -ex

sudo -u liquid-apps /opt/liquid-core/libexec/create-oauth-application "matrix" "{{ http_scheme }}://riot.{{ liquid_domain }}/__auth/callback"

echo "Creating secret keys..."
set +x
source /var/lib/liquid/oauth_keys/matrix
echo "LIQUID_CLIENT_ID = '$CLIENT_ID'" > /opt/matrix/authproxy/config/oauth.py
echo "LIQUID_CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/matrix/authproxy/config/oauth.py

if [ ! -s /opt/matrix/authproxy/config/secret.py ]; then
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/matrix/authproxy/config/secret.py
fi

set -x

supervisorctl start matrix-authproxy
