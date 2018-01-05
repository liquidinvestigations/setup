#!/bin/bash

set -e
set -x

if grep -qs -- '-- placeholder --' /opt/liquid-core/liquid-core/liquidcore/site/settings/secret_key.py; then
    # create secret keys without echoing
    set +x
    echo "SECRET_KEY = '`openssl rand -base64 48`'" > /opt/liquid-core/liquid-core/liquidcore/site/settings/secret_key.py
fi

cd /opt/liquid-core/liquid-core
../venv/bin/python ./manage.py migrate
chown liquid-apps: ../var/db.sqlite3

supervisorctl start liquid-core