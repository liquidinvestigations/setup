#!/bin/bash
set -e
set -x

cd /opt/hoover

if [ ! -s /opt/hoover/search/hoover/site/settings/secret_key.py ]; then
(
    # create secret keys without echoing
    set +x
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/hoover/search/hoover/site/settings/secret_key.py
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/hoover/snoop2/snoop/secret_key.py
)
fi

sudo -u liquid-apps /opt/liquid-core/libexec/create-oauth-application "hoover" "{{ http_scheme }}://hoover.{{ liquid_domain }}/accounts/oauth2-exchange/"
source /var/lib/liquid/oauth_keys/hoover
echo "CLIENT_ID = '$CLIENT_ID'" > /opt/hoover/search/hoover/site/settings/oauth.py
echo "CLIENT_SECRET = '$CLIENT_SECRET'" >> /opt/hoover/search/hoover/site/settings/oauth.py

# create and migrate dbs
sudo -u liquid-apps bash <<EOF
set -x
psql -lqt | cut -d \| -f 1 | grep -qw hoover-search || createdb hoover-search
psql -lqt | cut -d \| -f 1 | grep -qw hoover-snoop2 || createdb hoover-snoop2
/opt/hoover/bin/hoover search migrate
/opt/hoover/bin/hoover snoop2 migrate
EOF

# Start services
supervisorctl start hoover-elasticsearch hoover-search hoover-snoop2 hoover-tika
supervisorctl start hoover-snoop2-worker hoover-snoop2-updater hoover-search-updater
