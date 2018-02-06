import sys
import os
import json
from pathlib import Path
import subprocess
from images.builders.cloud import Builder_cloud
from .lan import configure_lan
from .wifi import configure_wifi
from .vpn import client
from . import discover

GLOBAL_LIQUID_OPTIONS = '/var/lib/liquid/conf/options.json'
CURRENT_LIQUID_VARS = '/var/lib/liquid/conf/vars.json'


def get_liquid_options():
    with open(GLOBAL_LIQUID_OPTIONS, encoding='utf8') as f:
        return json.load(f)


def get_current_vars():
    if not os.path.exists(CURRENT_LIQUID_VARS):
        return {}
    with open(CURRENT_LIQUID_VARS, encoding='utf8') as f:
        return json.load(f)


def write_current_vars(vars):
    tmp = CURRENT_LIQUID_VARS + '.tmp'
    with open(tmp, 'w', encoding='utf8') as f:
        print(json.dumps(vars), file=f)
    os.rename(tmp, CURRENT_LIQUID_VARS)


def run(cmd):
    print('+', cmd)
    subprocess.run(cmd, shell=True, check=True)


def ansible(vars, tags):
    builder = Builder_cloud()
    (builder.setup / 'ansible' / 'vars' / 'config.yml').touch()
    builder.update(tags, None, vars)


def on_reconfigure():
    print('on_reconfigure')
    options = json.load(sys.stdin)
    vars = {'liquid_{}'.format(k): v for k, v in options['vars'].items()}
    vars['liquid_apps'] = get_liquid_options().get('apps', True)

    old_vars = get_current_vars()
    first_boot = not old_vars

    print('old_vars:', json.dumps(old_vars))
    print('vars:', json.dumps(vars))

    changes = set()

    if vars['liquid_lan'] != old_vars.get('liquid_lan'):
        changes.add('lan')

    if vars['liquid_wan'] != old_vars.get('liquid_wan'):
        changes.add('wan')

    if vars['liquid_ssh'] != old_vars.get('liquid_ssh'):
        changes.add('ssh')

    if vars['liquid_vpn'] != old_vars.get('liquid_vpn'):
        changes.add('vpn')

    if vars['liquid_services'] != old_vars.get('liquid_services'):
        changes.add('services')

    print('changes:', changes)

    if first_boot:
        tags = 'configure'

    else:
        tags = ','.join('configure-{}'.format(c) for c in changes)

    print('tags:', tags)

    if tags:
        ansible(vars, tags)

    if changes.intersection({'services'}):
        run('/opt/common/initialize.sh')

    if changes.intersection({'lan'}):
        print('configure_lan')
        configure_lan(vars)

    if changes.intersection({'lan', 'wan'}):
        print('configure_wifi')
        configure_wifi(vars)

    if changes.intersection({'vpn'}):
        print('syncing vpn client keys')
        client.sync_keys(vars)

    if changes.intersection({'lan', 'wan', 'vpn'}):
        print('configuring avahi interfaces')
        discover.configure_avahi(vars)

    if changes.intersection({'ssh'}):
        if vars['liquid_ssh']['enabled']:
            run('systemctl reload-or-restart ssh')
        else:
            run('systemctl stop ssh')

    if changes.intersection({'services'}):
        run('service nginx restart')
        run('supervisorctl update')
        run('supervisorctl restart all')

    write_current_vars(vars)
