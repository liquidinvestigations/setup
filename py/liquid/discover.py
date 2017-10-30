import sys
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

    interfaces = (set(get_interfaces()) | set(['tun0', 'tun1'])) - set(['lo'])
    avahi_daemon_conf_txt = template.format(
        avahi_interfaces=','.join(interfaces),
    )

    with open(AVAHI_DAEMON_CONF, 'w', encoding='utf8') as f:
        f.write(avahi_daemon_conf_txt)


GLOBAL_LIQUID_OPTIONS = '/var/lib/liquid/conf/options.json'
DNSMASQ_COMMON_PATH = '/etc/NetworkManager/dnsmasq.d/liquid.conf'
DNSMASQ_HOTSPOT_PATH = '/etc/NetworkManager/dnsmasq-shared.d/liquid.conf'

DNSMASQ_COMMON = """\
domain-needed
bogus-priv
no-resolv
no-hosts
server=208.67.222.222
server=208.67.220.220
"""


def update():
    print('discover update')
    options = json.load(sys.stdin)

    with open(GLOBAL_LIQUID_OPTIONS, encoding='utf8') as f:
        my_domain = json.load(f)['domain']

    dns_list = []
    for node in options['nodes']:
        dns_list.append((node['hostname'], node['data']['address']))

    def dnsmasq_record(domain, address):
        return 'address=/{}/{}\n'.format(domain, address)

    with open(DNSMASQ_COMMON_PATH, 'w', encoding='latin1') as f:
        f.write(DNSMASQ_COMMON)
        f.write(dnsmasq_record(my_domain, '127.0.0.1'))
        for item in dns_list:
            f.write(dnsmasq_record(*item))

    with open(DNSMASQ_HOTSPOT_PATH, 'w', encoding='latin1') as f:
        f.write(dnsmasq_record(my_domain, '10.42.0.1'))
        for item in dns_list:
            f.write(dnsmasq_record(*item))

    subprocess.check_call(['killall', '-HUP', 'NetworkManager'])
