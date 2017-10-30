import json
import subprocess

AVAHI_DAEMON_CONF = '/etc/avahi/avahi-daemon.conf'
AVAHI_DAEMON_CONF_TMPL = '/etc/avahi/avahi-daemon.conf.tmpl'


def get_interfaces():
    out = subprocess.check_output([
        '/opt/discover/venv/bin/python', '-c',
        'import json, netifaces; print(json.dumps(netifaces.interfaces()))',
    ])
    return json.loads(out.decode('utf8'))


def configure_avahi(vars):
    with open(AVAHI_DAEMON_CONF_TMPL, encoding='utf8') as f:
        template = f.read()

    interfaces = set(get_interfaces()) - set(['lo']) + set(['tun0', 'tun1'])
    avahi_daemon_conf_txt = template.format(
        avahi_interfaces=','.join(interfaces),
    )

    with open(AVAHI_DAEMON_CONF, 'w', encoding='utf8') as f:
        f.write(avahi_daemon_conf_txt)
