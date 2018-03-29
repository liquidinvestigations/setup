#!/bin/bash
set -x

# Errors off, tasks that must be run before first boot
echo "Starting firewall"
/opt/common/libexec/firewall

echo "Looking for attached external storage..."
until /opt/setup/bin/external-storage; do
        echo 'waiting for external storage ...'
        sleep 20
done


systemctl start supervisor
supervisor_up() {
  ! supervisorctl status | grep -q 'supervisor\.sock no such file'
}
until supervisor_up; do echo 'waiting for supervisor ...'; sleep 1; done
echo 'supervisor up'
supervisorctl update
service postgresql start

FIRST_BOOT=NOT_STARTED

# Errors on, try to start first boot.
set -e
cd /opt/common
if [ ! -f /var/lib/liquid/first_boot_done ] && [ ! -f /var/lib/liquid/first_boot_failed ]; then
  echo "Starting first boot."
  if /opt/common/libexec/invoke-hook first-boot; then
    echo "First boot done."
    FIRST_BOOT=DONE
  else
    echo "First boot failed."
    FIRST_BOOT=FAILED
  fi
else
  FIRST_BOOT=ALREADY_DONE
  echo "Not starting first boot, already done."
  echo "Running initialize.sh"
 ./initialize.sh
fi

supervisorctl update
supervisorctl start all

# Mark first_boot_done and first_boot_failed only after the
# services have been started and hooks have been ran.
# This is important for the first boot tests, that wait
# for either first_boot_done or first_boot_failed to exist before
# starting The suite.
case "$FIRST_BOOT" in
  ALREADY_DONE)
    echo "First boot already done, not marking"
    ;;
  DONE)
    echo "Marking first_boot_done"
    touch /var/lib/liquid/first_boot_done
    ;;
  FAILED)
    echo "Marking first_boot_failed"
    touch /var/lib/liquid/first_boot_failed
    ;;
  *)
    echo "Unknown FIRST_BOOT flag, marking first_boot_failed"
    touch /var/lib/liquid/first_boot_failed
    ;;
esac

echo "Boot scripts done."
