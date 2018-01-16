from pathlib import Path
from .builders.cloud import Builder_cloud
from .builders.odroid import Builder_odroid_c2, Builder_odroid_xu4
from .builders.pine64 import Builder_rock64

FLAVOURS = {
    'cloud': Builder_cloud,
    'odroid_c2': Builder_odroid_c2,
    'odroid_xu4': Builder_odroid_xu4,
    'rock64': Builder_rock64,
}


def build(flavor, tags, skip_tags, apps, image_path, image_size):
    builder_cls = FLAVOURS[flavor]
    builder = builder_cls()
    builder.install_ansible()

    if image_path:
        image = Path(image_path).resolve()

    else:
        builder.install_qemu_utils()
        image = builder.prepare_image(image_size)

    builder.build(image, tags, skip_tags, {'liquid_apps': apps})


def install(tags=None, skip_tags=None):
    builder = Builder_cloud()
    (builder.setup / 'ansible' / 'vars' / 'config.yml').touch()
    builder.update(tags, skip_tags, {'liquid_apps': True})
