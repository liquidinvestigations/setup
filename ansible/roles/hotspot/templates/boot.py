#!/usr/bin/env python3

import sys
import re
from pathlib import Path
import subprocess

RUN_DIR = Path('/var/local/hotspot/run')
SUPERVISOR_DIR = Path('/etc/supervisor/conf.d')

HOSTAPD_CONFIG_TEMPLATE = """\
interface={interface}

ieee80211d=1
country_code={country_code}
ieee80211n=1
wmm_enabled=1

driver=nl80211
hw_mode=g
ssid={ssid}

channel={channel}

auth_algs=1
wpa=2
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
wpa_passphrase={passphrase}
"""

HOSTAPD_SUPERVISOR_TEMPLATE = """\
[program:{program_name}]
command = /usr/sbin/hostapd -d {hostapd_conf_path}
autostart = false
startsecs = 3
"""

DNSMASQ_CONFIG_TEMPLATE = """\
interface=br0
bind-interfaces
domain-needed
bogus-priv
no-resolv
no-poll
no-hosts
server=8.8.8.8
address=/liquid/{liquid_address}
dhcp-range={dhcp_range},12h
"""

DNSMASQ_SUPERVISOR_TEMPLATE = """\
[program:dnsmasq]
command = /usr/sbin/dnsmasq --keep-in-foreground -C {dnsmasq_conf_path}
autostart = false
startsecs = 3
"""

def find_wireless_interfaces():
    iwconfig = (
        subprocess
        .check_output(['iwconfig'], stderr=subprocess.DEVNULL)
        .decode('latin1')
    )
    for line in iwconfig.splitlines():
        m = re.match('(\w+)', line)
        if m:
            yield m.group(1)

def boot_hostapd(interface):
    hostapd_conf_path = RUN_DIR / 'hostapd-{}.conf'.format(interface)
    supervisor_conf_path = SUPERVISOR_DIR / 'hostapd-{}.conf'.format(interface)
    program_name = 'hostapd-' + interface

    hostapd_conf = HOSTAPD_CONFIG_TEMPLATE.format(
        interface=interface,
        country_code='RO',
        channel='6',
        ssid='liquid',
        passphrase='chocolate',
    )
    with hostapd_conf_path.open('wt', encoding='utf8') as f:
        f.write(hostapd_conf)

    supervisor_conf = HOSTAPD_SUPERVISOR_TEMPLATE.format(
        program_name=program_name,
        hostapd_conf_path=hostapd_conf_path,
    )
    with supervisor_conf_path.open('wt', encoding='utf8') as f:
        f.write(supervisor_conf)

    subprocess.check_call(['supervisorctl', 'update'])
    subprocess.check_call(['supervisorctl', 'start', program_name])
    subprocess.check_call(['brctl', 'addif', 'br0', interface])

def boot_dnsmasq(liquid_address, dhcp_range):
    dnsmasq_conf_path = RUN_DIR / 'dnsmasq.conf'
    supervisor_conf_path = SUPERVISOR_DIR / 'dnsmasq.conf'

    dnsmasq_conf = DNSMASQ_CONFIG_TEMPLATE.format(
        dhcp_range=dhcp_range,
        liquid_address=liquid_address,
    )
    with dnsmasq_conf_path.open('wt', encoding='utf8') as f:
        f.write(dnsmasq_conf)

    supervisor_conf = DNSMASQ_SUPERVISOR_TEMPLATE.format(
        dnsmasq_conf_path=dnsmasq_conf_path,
    )
    with supervisor_conf_path.open('wt', encoding='utf8') as f:
        f.write(supervisor_conf)

    subprocess.check_call(['supervisorctl', 'update'])
    subprocess.check_call(['supervisorctl', 'start', 'dnsmasq'])

def main():
    subprocess.check_call(['rm', '-rf', str(RUN_DIR)])
    subprocess.check_call(['rm', '-f', str(SUPERVISOR_DIR / 'hostapd-*.conf')])
    subprocess.check_call(['mkdir', '-p', str(RUN_DIR)])

    subprocess.check_call(['brctl', 'addbr', 'br0'])
    subprocess.check_call([
        'ifconfig', 'br0',
        '10.102.0.1', 'netmask', '255.255.255.0',
    ])

    interfaces = list(find_wireless_interfaces())
    if not interfaces:
        print("no wireless interfaces found", file=sys.stderr)
        return

    boot_hostapd(interfaces[0])
    boot_dnsmasq('10.102.0.1', '10.102.0.100,10.102.0.200')

if __name__ == '__main__':
    main()
