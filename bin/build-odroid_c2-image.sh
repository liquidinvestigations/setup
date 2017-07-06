#!/bin/bash

###
# Build a Liquid image and save it to `shared/output`
###

set -e

SETUPDIR=/mnt/shared/setup
TARGET=/mnt/target
TEMPDIR=/tmp
OUTPUT=/mnt/shared/output

set -x

apt-add-repository -y ppa:ansible/ansible
apt-get update
apt-get install -y ansible git pv

curl https://liquidinvestigations.org/images/ubuntu64-16.04-minimal-odroid-c2-20160815-4G.img.xz | xzcat > $TEMPDIR/odroid-c2.img

losetup /dev/loop0 $TEMPDIR/odroid-c2.img -o 135266304
mkdir -p $TARGET
mount /dev/loop0 $TARGET
mount --bind /proc $TARGET/proc
echo "nameserver 8.8.8.8" > $TARGET/etc/resolv.conf

chroot $TARGET apt-get update
chroot $TARGET apt-get install -y python
chroot $TARGET apt-get clean

cd $SETUPDIR/ansible
touch vars/config.yml
ansible-playbook image_chroot.yml

umount $TARGET/proc
umount $TARGET
losetup -d /dev/loop0

mkdir -p $OUTPUT
pv < $TEMPDIR/odroid-c2.img | xz -0 > $OUTPUT/odroid-c2-liquid.img.xz
