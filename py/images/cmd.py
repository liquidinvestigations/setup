from argparse import ArgumentParser
from . import setup
from . import tools


def build_image():
    parser = ArgumentParser()
    parser.add_argument('flavor', choices=setup.FLAVOURS.keys())
    parser.add_argument('-d', '--debug', action='store_true')
    options = parser.parse_args()
    tools.DEBUG = options.debug
    setup.build(options.flavor)


def install():
    setup.install()
