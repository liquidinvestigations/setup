#!/bin/bash
set -e

cd /opt/hoover

sudo -u liquid bash <<EOF
psql -lqt | cut -d \| -f 1 | grep -qw hoover-search || createdb hoover-search
psql -lqt | cut -d \| -f 1 | grep -qw hoover-snoop || createdb hoover-snoop
/opt/hoover/bin/hoover search migrate
/opt/hoover/bin/hoover snoop migrate
EOF

