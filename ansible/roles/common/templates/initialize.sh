#!/bin/bash
set -e

#sudo -u postgres createuser --superuser liquid

for file in /opt/common/initialize.d/*
do
  "$file"
done
