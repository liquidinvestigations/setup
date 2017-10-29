import os
import json
from pathlib import Path
import subprocess
import shutil

VAR = Path('/var/lib/liquid/vpn')
CA = VAR / 'ca'
CA_KEYS = CA / 'keys'
SERVER = VAR / 'server'
SERVER_KEYS = SERVER / 'keys'

CA_VARS = {
    'KEY_SIZE': '2048',
    'CA_EXPIRE': '3650',
    'KEY_EXPIRE': '3650',
    'KEY_COUNTRY': 'US',
    'KEY_PROVINCE': 'MI',
    'KEY_CITY': 'Detroit',
    'KEY_ORG': 'LiquidInvestigations',
    'KEY_EMAIL': 'support@liquiddemo.org',
    'KEY_OU': 'node',
    'KEY_NAME': 'detroit-liquid.local'
}


def run(cmd, encoding='latin1', **kwargs):
    print('+', ' '.join(cmd))
    output = subprocess.check_output(cmd, **kwargs)
    return output.decode(encoding).strip()


def easyrsa_env():
    env = dict(os.environ)

    env.update({
        'EASY_RSA': str(CA),
        'OPENSSL': 'openssl',
        'PKCS11TOOL': 'pkcs11-tool',
        'GREP': 'grep',
    })

    env.update({
        'KEY_CONFIG': run([str(CA / 'whichopensslcnf'), str(CA)], env=env),
        'KEY_DIR': str(CA_KEYS),
        'PKCS11_MODULE_PATH': 'dummy',
        'PKCS11_PIN': 'dummy',
    })

    env.update(CA_VARS)

    return env


def copy_openvpn_keys():
    """
    OpenVPN runs as user `nobody`. Copy its certificates to a place where it
    can read them.
    """
    keys = [
        'ca.crt', 'server.crt', 'server.key',
        'dh2048.pem', 'crl.pem', 'ta.key',
    ]
    for filename in keys:
        shutil.copy(str(CA_KEYS / filename), str(SERVER_KEYS / filename))


def set_up_easyrsa():
    run(['make-cadir', str(CA)])

    env = easyrsa_env()

    def run_ca(*args, **kwargs):
        kwargs['cwd'] = str(CA)
        kwargs['env'] = env
        return run(*args, **kwargs)

    run_ca(['./clean-all'])
    run_ca(['./pkitool', '--initca'])
    run_ca(['./pkitool', '--server', 'server'])

    dh_file = str(CA_KEYS / 'dh{KEY_SIZE}.pem'.format(**env))
    run_ca([
        'openssl', 'dhparam',
        '-dsaparam',  # https://security.stackexchange.com/a/95184
        '-out', dh_file,
        env['KEY_SIZE'],
    ])

    hmac_file = str(CA_KEYS / 'ta.key')
    run_ca(['openvpn', '--genkey', '--secret', hmac_file])

    env['KEY_CN'] = 'Liquid Investigations'
    env['KEY_ALTNAMES'] = 'something'
    run_ca([
        'openssl', 'ca', '-gencrl',
        '-out', str(CA_KEYS / 'crl.pem'),
        '-config', env['KEY_CONFIG'],
    ])

    copy_openvpn_keys()


def initialize():
    if not CA.exists():
        try:
            set_up_easyrsa()
        except:
            shutil.rmtree(str(CA))
            raise
