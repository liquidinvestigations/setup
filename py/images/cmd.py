from argparse import ArgumentParser
from . import setup
from . import tools


def build_image():
    parser = ArgumentParser()
    parser.add_argument('flavor', choices=setup.FLAVOURS.keys())
    parser.add_argument('--tags', default=None)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--image', default=None)
    parser.add_argument('--no-docker', dest='docker', action='store_false')
    options = parser.parse_args()
    tools.DEBUG = options.debug
    setup.build(options.flavor, options.tags, options.image, options.docker)


def install():
    parser = ArgumentParser()
    parser.add_argument('--tags', default=None)
    options = parser.parse_args()
    setup.install(options.tags)
