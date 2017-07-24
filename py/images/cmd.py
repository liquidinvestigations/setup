from argparse import ArgumentParser
from .builders.cloud import Builder_cloud
from .builders.odroid import Builder_odroid_c2, Builder_odroid_xu4
from . import tools

FLAVORS = {
    'cloud': Builder_cloud,
    'odroid_c2': Builder_odroid_c2,
    'odroid_xu4': Builder_odroid_xu4,
}


def main():
    parser = ArgumentParser()
    parser.add_argument('flavor', choices=FLAVORS.keys())
    parser.add_argument('-d', '--debug', action='store_true')
    options = parser.parse_args()
    builder_cls = FLAVORS[options.flavor]
    tools.DEBUG = options.debug
    builder_cls().build()
