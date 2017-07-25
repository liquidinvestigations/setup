from ..tools import download, xzcat
from .base import BaseBuilder, SHARED


class Builder_odroid_c2(BaseBuilder):

    def get_base_image(self):
        base_image_url = (
            'https://liquidinvestigations.org/images/base_images/'
            'ubuntu64-16.04-minimal-odroid-c2-20160815.img.xz'
        )
        base_image = SHARED / 'xenial-odroid_c2-minimal.img.xz'
        download(base_image_url, base_image)

        image = SHARED / 'ubuntu-odroid_c2-raw.img'
        xzcat(base_image, image)

        return (image, 135266304)


class Builder_odroid_xu4(BaseBuilder):

    def get_base_image(self):
        base_image_url = (
            'https://liquidinvestigations.org/images/base_images/'
            'ubuntu-16.04.2-minimal-odroid-xu4-20170516.img.xz'
        )
        base_image = SHARED / 'xenial-odroid_xu4-minimal.img.xz'
        download(base_image_url, base_image)

        image = SHARED / 'ubuntu-odroid_xu4-raw.img'
        xzcat(base_image, image)

        return (image, 135266304)
