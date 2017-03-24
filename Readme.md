## Set up a liquid image based on a fresh ubuntu image:

* Get a fresh Ubuntu Xenial image from `http://de.eu.odroid.in/ubuntu_16.04lts/`:

   ```
   curl 'http://de.eu.odroid.in/ubuntu_16.04lts/ubuntu64-16.04-minimal-odroid-c2-20160815.img.xz' | xzcat > ubuntu64-16.04-minimal-odroid-c2-20160815.img
   curl 'http://de.eu.odroid.in/ubuntu_16.04lts/ubuntu64-16.04-minimal-odroid-c2-20160815.img.md5sum' | md5sum -c -
   ```

* Calculate the offset of the root filesystem and mount it:

   ```
   fdisk -lu ubuntu64-16.04-minimal-odroid-c2-20160815.img
   # e.g. sector size 512, 2nd partition starts at sector 264192, so
   # the offset is 264192 * 512 = 135266304
   losetup /dev/loop0 ubuntu64-16.04-minimal-odroid-c2-20160815.img -o 135266304
   mount /dev/loop0 /var/local/liquid/target
   ```

* Run the ansible playbook:

   ```
   cd liquid-setup/ansible
   sudo ansible-playbook image.yml
   ```

## Set up the bundle on the local system:
```
cd liquid-setup/ansible
sudo ansible-playbook local.yml
```
