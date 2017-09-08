from ..tools import download, run
from .base import BaseBuilder, SHARED


class Builder_cloud(BaseBuilder):

    OFFSET = 1048576

    def get_base_image(self):
        base_image_url = (
            'https://liquidinvestigations.org/images/base_images/'
            'ubuntu-16.04-server-cloudimg-amd64-disk1.img'
        )
        base_image = SHARED / 'ubuntu-x86_64-cow2.img'
        download(base_image_url, base_image)

        image = SHARED / 'ubuntu-x86_64-raw.img'
        run([
            'qemu-img', 'convert',
            '-f', 'qcow2',
            '-O', 'raw',
            str(base_image),
            str(image),
        ])

        return (image, self.OFFSET)

    def _patch_serial_console(self, target):
        """
        `console=` setting referencing non-existant port can cause hangs during
        boot: https://bugs.launchpad.net/cloud-images/+bug/1573095
        """
        run([
            'sed', '-i',
            's/console=hvc0 *//g',
            str(target.mount_point / 'boot/grub/menu.lst'),
        ])

        grub_files = [
            'boot/grub/grub.cfg',
            'etc/default/grub',
            'etc/default/grub.d/50-cloudimg-settings.cfg',
        ]
        for rel_path in grub_files:
            path = target.mount_point / rel_path
            run(['sed', '-i', 's/ *console=ttyS0//g', str(path)])

    def install(self, target):
        super().install(target)
        self._patch_serial_console(target)
        (target.mount_point / 'etc/cloud/cloud-init.disabled').touch()
