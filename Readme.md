## Requirements

* ansible 2.2 or newer

## Set up a microboard image based on a fresh ubuntu image:

* Get a fresh Ubuntu Xenial image from `http://de.eu.odroid.in/ubuntu_16.04lts/`:

   ```
   curl 'http://de.eu.odroid.in/ubuntu_16.04lts/ubuntu64-16.04-minimal-odroid-c2-20160815.img.xz' | xzcat > ubuntu64-16.04-minimal-odroid-c2-20160815.img
   curl 'http://de.eu.odroid.in/ubuntu_16.04lts/ubuntu64-16.04-minimal-odroid-c2-20160815.img.md5sum' | md5sum -c -
   mv ubuntu64-16.04-minimal-odroid-c2-20160815.img liquid.img
   ```

* Enlarge the image, we need at least 2GB to be safe:

   ```
   truncate liquid-image.img --size=2G
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
   # e.g. sector size 512, 2nd partition starts at sector 264192, so
   # the offset is 264192 * 512 = 135266304
   losetup /dev/loop0 liquid.img -o 135266304
   mount /dev/loop0 /var/local/liquid/target
   mount --bind /proc /var/local/liquid/target/proc
   resize2fs /dev/loop0
   ```

* Run the ansible playbook:

   ```
   cd liquid-setup/ansible
   sudo ansible-playbook board_chroot.yml
   ```

## Upgrade an existing installation on a microboard:
```
cd liquid-setup/ansible
sudo ansible-playbook board_local.yml
```

## Set up the bundle on a cloud server:
```
cd liquid-setup/ansible
sudo ansible-playbook server.yml
```
