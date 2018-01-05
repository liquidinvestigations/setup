#!/bin/bash
set -e
set -x

date

sudo -u postgres psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='liquid-apps'" | grep -q 1 || sudo -u postgres createuser --superuser liquid-apps

INITIALIZE_RESULT=0

set +e
for file in /opt/common/initialize.d/*
do
  "$file"
  RESULT=$?
  if [ 0 -ne $RESULT ]; then
      INITIALIZE_RESULT=$RESULT
  fi
  echo "$file $RESULT"
done
set -e

echo "$0 $INITIALIZE_RESULT"

exit $INITIALIZE_RESULT
