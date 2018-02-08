import sys
import re
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
    vpn_server_address = OPTIONS['vpn']['server']['address']
    return CLIENT_OVPN_TEMPLATE.format(
        address=vpn_server_address['address'],
        port=vpn_server_address['port'],
        ca_cert=read_key('ca.crt'),
        client_cert=read_key('client-{}.crt'.format(name)),
        client_key=read_key('client-{}.key'.format(name)),
        ta_key=read_key('ta.key'),
    )


def run(cmd, encoding='latin1', **kwargs):
    print('+', ' '.join(cmd))
    output = subprocess.check_output(cmd, **kwargs)
    return output.decode(encoding).strip()


def create(id):
    env = ca.easyrsa_env()
    run(['./pkitool', 'client-{}'.format(id)], cwd=str(ca.CA), env=env)


def get_key_map():
    rv = {}

    with (ca.CA_KEYS / 'index.txt').open(encoding='utf8') as f:
        for line in f:
            cols = line.split('\t')
            serial = cols[3]
            match = re.search(r'/CN=client-(?P<id>\d+)/', cols[5])
            if match:
                id = match.group('id')
                rv[serial] = id

    return rv


def get_revoked_serials():
    crl_pem = str(ca.CA_KEYS / 'crl.pem')
    txt = run(['openssl', 'crl', '-in', crl_pem, '-text'])

    skip = True
    for line in txt.splitlines():
        if line == 'Revoked Certificates:':
            skip = False
            continue
        if skip:
            continue
        if not line.startswith(' '):
            break
        match = re.match(r'^\s+Serial Number:\s+(?P<serial>\S+)$', line)
        if match:
            yield match.group('serial')


def get_keys():
    rv = set()
    for item in ca.CA_KEYS.iterdir():
        match = re.match(r'^client-(?P<id>.+)\.crt$', item.name)
        if match:
            rv.add(match.group('id'))
    return rv


def get_revoked():
    key_map = get_key_map()
    rv = set()
    for serial in get_revoked_serials():
        rv.add(key_map[serial])
    return rv


def revoke(id):
    env = ca.easyrsa_env()

    try:
        run(['./revoke-full', 'client-{}'.format(id)], cwd=str(ca.CA), env=env)
    except subprocess.CalledProcessError:
        # yes, `revoke-full` returns code 2 when it does its job successfully.
        # https://is.gd/openvpn_revoke
        pass

    if id not in get_revoked():
        raise RuntimeError('The key {} was not revoked'.format(id))

    ca.copy_openvpn_keys()


def sync_keys(vars):
    ca_keys = get_keys()
    ca_revoked = get_revoked()

    liquidcore_keys = (
        vars
        .get('liquid_vpn', {})
        .get('server', {})
        .get('client_keys', [])
    )

    for key in liquidcore_keys:
        (id, revoked) = (key['id'], key['revoked'])

        if id not in ca_keys:
            print('creating vpn client key', id)
            create(id)

        if revoked and id not in ca_revoked:
            print('revoking vpn client key', id)
            revoke(id)
