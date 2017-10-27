import sys
import json
from pathlib import Path
import subprocess
from images.setup import install
from .wifi import configure_wifi
from .vpn import client

ANSIBLE_VARS = Path(__file__).parent.parent.parent / 'ansible' / 'vars'

def run(cmd):
    print('+', cmd)
    subprocess.run(cmd, shell=True, check=True)


def on_reconfigure():
    print('on_reconfigure')
    options = json.load(sys.stdin)
    vars = {'liquid_{}'.format(k): v for k, v in options['vars'].items()}

    vars_path = ANSIBLE_VARS / 'liquidcore.yml'
    with vars_path.open('w', encoding='utf8') as f:
        print(json.dumps(vars, indent=2, sort_keys=True), file=f)

    install(tags='configure')
    run('/opt/common/initialize.sh')

    print('configure_wifi')
    configure_wifi(vars)

    print('syncing vpn client keys')
    client.sync_keys(vars)

    run('service nginx reload')
    run('supervisorctl update')
    run('supervisorctl restart all')
