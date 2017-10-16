#!/bin/bash
set -x

# Errors off, tasks that must be run before first boot
echo "Starting firewall"
/opt/common/libexec/firewall

supervisor_up() {
  ! supervisorctl status | grep -q 'supervisor\.sock no such file'
}
until supervisor_up; do echo 'waiting for supervisor ...'; sleep 1; done
echo 'supervisor up'
supervisorctl update
service postgresql start

# Errors on, try to start first boot.
set -e
cd /opt/common
if [ ! -f first_boot_done ] && [ ! -f first_boot_failed ]; then
  echo "Starting first boot."
  if ./initialize.sh ; then
    echo "First boot done."
    touch first_boot_done
  else
    echo "First boot failed."
    touch first_boot_failed
  fi
else
  echo "Not starting first boot, already done."
fi

# Errors off, start services and run on-boot hooks.
set +e
echo "Starting all services."
# TODO: only start enabled services
supervisorctl start all

supervisorctl restart dnsmasq-dns

echo "Running on-boot hook."
for file in /opt/common/hooks/on-boot.d/*
do
  "$file"
done

echo "Boot scripts done."
