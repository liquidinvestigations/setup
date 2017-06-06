# Liquid Investigations: Software Stack Setup
This repository contains [ansible](http://docs.ansible.com/ansible/) scripts
that set up the software stack for liquid investigations. It's designed to work
in two scenarios: installation on a server or VPS, and preparing an OS image
for an ARM64 microboard.

Find more information about the Liquid Investigations project on the
[home page](https://liquidinvestigations.org/wordpress).


## Requirements
* ansible 2.2 or newer
* ARM Boards: Ubuntu 16.04 LTS (Xenial), Cloud Servers: Debian 8.7 (Jessie)


## Configuration
The ansible playbooks read configuration from `ansible/vars/defaults.yml` and
`ansible/vars/config.yml`. The `config.yml` file does not exist initially, so
you need to create it. Let's set a custom domain name for our build:

```shell
echo "liquid_domain: odroid.liquid" > ansible/vars/config.yml
```

You may use it to override any variables you want from `config.yml`.


### Set up a microboard image based on a fresh ubuntu image:
* Make sure there are no services (postgresql, elasticsearch, etc) running on
  the host system as they may interfere with packages installed in the chroot
  image.

* Get a fresh Ubuntu Xenial image from `http://de.eu.odroid.in/ubuntu_16.04lts/`:

   ```
   curl 'http://de.eu.odroid.in/ubuntu_16.04lts/ubuntu64-16.04-minimal-odroid-c2-20160815.img.xz' | xzcat > ubuntu64-16.04-minimal-odroid-c2-20160815.img
   curl 'http://de.eu.odroid.in/ubuntu_16.04lts/ubuntu64-16.04-minimal-odroid-c2-20160815.img.md5sum' | md5sum -c -
   mv ubuntu64-16.04-minimal-odroid-c2-20160815.img liquid.img
   ```

* Enlarge the image, we need at least 3GB to be safe:

   ```
   truncate liquid.img --size=3G
   fdisk liquid.img
   ```

  In the interactive shell of fdisk, run these commands:

   ```
   d
   2
   n
   p
   2
   <enter>
   <enter>
   ```

* Calculate the offset of the root filesystem and mount it:

   ```
   fdisk -lu liquid.img
   # e.g. sector size 512
   # 1st partition starts at 2048, offset is 2048 * 512 = 1048576
   # 2nd partition starts at 264192, offset is 264192 * 512 = 135266304
   losetup /dev/loop0 liquid.img -o 1048576
   losetup /dev/loop1 liquid.img -o 135266304
   mount /dev/loop1 /mnt/target
   mount /dev/loop0 /mnt/target/media/boot
   mount --bind /proc /mnt/target/proc
   resize2fs /dev/loop1
   ```

* Upgrade the base packages, because `bootini` displays an interactive message,
  and blocks when upgraded from ansible. Also, install python 2.7:

   ```
   chroot /mnt/target
   apt-get update
   apt-get upgrade -y
   apt-get install -y python
   apt-get clean
   exit
   ```

* Run the ansible playbook:

   ```
   cd liquid-setup/ansible
   sudo ansible-playbook board_chroot.yml
   ```


### Upgrade an existing installation on a microboard:
```
cd liquid-setup/ansible
sudo ansible-playbook board_local.yml
```


### Set up the bundle on a cloud server:
```
cd liquid-setup/ansible
sudo ansible-playbook server.yml
```

Note: `non-free` package sources must be used for Debian.


## First boot
On first (re)boot, the bundle will configure databases, and import the
[testdata](https://github.com/hoover/testdata) collection into Hoover. This
will take a few minutes. You can follow the progress in the log file:

```
tail -f /var/log/rc.local.log
```

When the initialization scripts compete successfully, they will create the file
`/opt/common/first_boot_done`, so they don't run on the next boot.

### hotspot
After the first-boot scripts complete, the system will attempt to create a
wireless hotspot, if it detecs any AP-capable wireless interfaces. The SSID is
`liquid`, password `chocolate`.

### Hoover and Hypothesis
By default, Hoover and Hypothesis are not started. To start them:

```
supervisorctl start hoover-elasticsearch hoover-search hoover-snoop hoover-tika
supervisorctl start hypothesis-beat hypothesis-elasticsearch hypothesis-web hypothesis-websocket hypothesis-worker
```
