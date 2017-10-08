from .builders.cloud import Builder_cloud
from .builders.odroid import Builder_odroid_c2, Builder_odroid_xu4

FLAVOURS = {
    'cloud': Builder_cloud,
    'odroid_c2': Builder_odroid_c2,
    'odroid_xu4': Builder_odroid_xu4,
}


def build(flavor, tags):
    builder_cls = FLAVOURS[flavor]
    builder_cls().build(tags)


def install(tags):
    builder = Builder_cloud()
    builder.install_ansible()
    (builder.setup / 'ansible' / 'vars' / 'config.yml').touch()
    builder.run_ansible('server.yml', tags)
