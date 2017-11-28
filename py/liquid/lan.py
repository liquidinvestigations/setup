import subprocess
from collections import defaultdict

ETHERNET_INTERFACE = 'eth0'


def brctl(*args):
    cmd = ['brctl'] + list(args)
    print('+', ' '.join(cmd))
    return subprocess.check_output(cmd).decode('latin1')


def get_bridge_interfaces():
    bridge_name = None
    bridges = defaultdict(list)

    for line in brctl('show').splitlines()[1:]:
        bits = line.split()
        if len(bits) > 1:
            bridge_name = bits[0]

        interface = bits[-1]
        bridges[bridge_name].append(interface)

    return dict(bridges)


def configure_lan(vars):
    lan_interfaces = get_bridge_interfaces().get('lan', [])
    liquid_lan = vars.get('liquid_lan', {})

    if liquid_lan.get('eth'):
        if ETHERNET_INTERFACE not in lan_interfaces:
            brctl('addif', 'lan', ETHERNET_INTERFACE)

    else:
        if ETHERNET_INTERFACE in lan_interfaces:
            brctl('delif', 'lan', ETHERNET_INTERFACE)

    lan_address = liquid_lan.get('ip')
    lan_netmask = liquid_lan.get('netmask')
    if lan_address and lan_netmask:
        subprocess.run([
            'ifconfig', 'lan',
            lan_address,
            'netmask', lan_netmask,
        ], check=True)
