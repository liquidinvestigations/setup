#!/bin/bash
set -e
set -x

date

supervisor_up() {
  ! supervisorctl status | grep -q 'supervisor\.sock no such file'
}
until supervisor_up; do echo 'waiting for supervisor ...'; sleep 1; done
echo 'supervisor up'
supervisorctl update

service postgresql start

sudo -u postgres psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='liquid'" | grep -q 1 || sudo -u postgres createuser --superuser liquid

for file in /opt/common/initialize.d/*
do
  "$file"
done

date
