import sys
import json
import subprocess
from . import ca

with open('/var/lib/liquid/conf/options.json', encoding='utf8') as f:
    OPTIONS = json.load(f)

CLIENT_OVPN_TEMPLATE = """\
client
dev tun
proto udp
remote {address} {port}
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
comp-lzo
verb 3
key-direction 1

<ca>
{ca_cert}
</ca>

<cert>
{client_cert}
</cert>

<key>
{client_key}
</key>

<tls-auth>
{ta_key}
</tls-auth>
"""


def read_key(name):
    with (ca.CA_KEYS / name).open(encoding='utf8') as f:
        return f.read().strip()


def generate_config(name):
    return CLIENT_OVPN_TEMPLATE.format(
        address=OPTIONS['domain'],
        port=1194,
        ca_cert=read_key('ca.crt'),
        client_cert=read_key('client-{}.crt'.format(name)),
        client_key=read_key('client-{}.key'.format(name)),
        ta_key=read_key('ta.key'),
    )


def run(cmd, encoding='latin1', **kwargs):
    print('+', ' '.join(cmd))
    output = subprocess.check_output(cmd, **kwargs)
    return output.decode(encoding).strip()


def create(name):
    env = ca.easyrsa_env()
    run(['./pkitool', 'client-{}'.format(name)], cwd=str(ca.CA), env=env)
