from ..tools import download, xzcat, run
from .base import BaseBuilder, Platform, IMAGES


class Platform_rock64(Platform):

    offset = 134217728

    def get_base_image(self):
        base_image_url = (
            'https://jenkins.liquiddemo.org/__images__/base/'
            'xenial-minimal-rock64-0.5.15-136-arm64.img.xz'
        )
        base_image = IMAGES / 'xenial-rock64-minimal.img.xz'
        download(base_image_url, base_image)

        image = IMAGES / 'ubuntu-rock64-raw.img'
        xzcat(base_image, image)

        return image


class Builder_rock64(BaseBuilder):

    platform = Platform_rock64()
