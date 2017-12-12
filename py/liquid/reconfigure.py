import sys
import json
from pathlib import Path
import subprocess
from images.builders.cloud import Builder_cloud
from .wifi import configure_wifi
from .vpn import client
from . import discover

GLOBAL_LIQUID_OPTIONS = '/var/lib/liquid/conf/options.json'


def get_liquid_options():
    with open(GLOBAL_LIQUID_OPTIONS, encoding='utf8') as f:
        return json.load(f)


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
    vars['liquid_apps'] = get_liquid_options().get('apps', True)

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
