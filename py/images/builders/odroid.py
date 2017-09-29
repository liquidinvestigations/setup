from ..tools import download, xzcat, run
from .base import BaseBuilder, IMAGES


class Builder_odroid_c2(BaseBuilder):

    def get_base_image(self):
        base_image_url = (
            'https://liquidinvestigations.org/images/base_images/'
            'ubuntu64-16.04-minimal-odroid-c2-20160815.img.xz'
        )
        base_image = IMAGES / 'xenial-odroid_c2-minimal.img.xz'
        download(base_image_url, base_image)

        image = IMAGES / 'ubuntu-odroid_c2-raw.img'
        xzcat(base_image, image)

        return (image, 135266304)


class Builder_odroid_xu4(BaseBuilder):

    def get_base_image(self):
        base_image_url = (
            'https://liquidinvestigations.org/images/base_images/'
            'ubuntu-16.04.2-minimal-odroid-xu4-20170516.img.xz'
        )
        base_image = IMAGES / 'xenial-odroid_xu4-minimal.img.xz'
        download(base_image_url, base_image)

        image = IMAGES / 'ubuntu-odroid_xu4-raw.img'
        xzcat(base_image, image)

        return (image, 135266304)

    def _fix_network(self, target):
        run(['apt-get', '-qq', 'purge', '--auto-remove', 'network-manager'])
        eth0_conf = target.mount_point / 'etc/network/interfaces.d/eth0'
        with eth0_conf.open('w', encoding='utf8') as f:
            f.write('auto eth0\niface eth0 inet dhcp\n')

    def install(self, target):
        super().install(target)
        self._fix_network(target)
