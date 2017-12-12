import sys
import json
from pathlib import Path
import subprocess
from images.builders.cloud import Builder_cloud
from .wifi import configure_wifi
from .vpn import client
from . import discover


def run(cmd):
    print('+', cmd)
    subprocess.run(cmd, shell=True, check=True)


def ansible(vars):
    builder = Builder_cloud()
    (builder.setup / 'ansible' / 'vars' / 'config.yml').touch()
    builder.update('configure', None, vars)


def on_reconfigure():
    print('on_reconfigure')
    options = json.load(sys.stdin)
    vars = {'liquid_{}'.format(k): v for k, v in options['vars'].items()}

    ansible(vars)
    run('/opt/common/initialize.sh')

    print('configure_wifi')
    configure_wifi(vars)

    print('syncing vpn client keys')
    client.sync_keys(vars)

    print('configuring avahi interfaces')
    discover.configure_avahi(vars)

    run('service nginx restart')
    run('supervisorctl update')
    run('supervisorctl restart all')
