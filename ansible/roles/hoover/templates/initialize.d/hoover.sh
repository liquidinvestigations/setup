#!/bin/bash
set -e

cd /opt/hoover

sudo -u liquid bash <<EOF
createdb hoover-search
createdb hoover-snoop
EOF

/opt/hoover/bin/hoover upgrade
