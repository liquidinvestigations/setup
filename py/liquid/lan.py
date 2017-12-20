from .network_manager import nmcli
from .network_manager import get_connections
from .network_manager import get_connection_properties

ETHERNET_INTERFACE = 'eth0'


def get_bridge_interfaces():
    connections = list(get_connections())
    rv = {}

    for item in connections:
        if item['type'] == 'bridge':
            rv[item['name']] = {}

    for item in connections:
        if item['type'] == '802-3-ethernet':
            properties = get_connection_properties(item['uuid'])
            if properties.get('connection.slave-type') == 'bridge':
                bridge_name = properties['connection.master']
                interface = properties['connection.interface-name']
                rv[bridge_name][interface] = item['uuid']

    return rv


def get_netmask_bits(netmask):
    """ Count the number of bits in the netmask """
    rv = 0
    stop = False
    for chunk in netmask.split('.'):
        byte = int(chunk)
        for bit in reversed(range(8)):
            if byte & 2**bit:
                if stop:
                    raise RuntimeError("One bit after zero bit")
                rv += 1
            else:
                stop = True
    return rv


def configure_lan(vars):
    liquid_lan = vars.get('liquid_lan', {})
    bridge_interfaces = get_bridge_interfaces()

    if 'lan' not in bridge_interfaces:
        lan_address = liquid_lan.get('ip')
        lan_netmask = liquid_lan.get('netmask')

        if not (lan_address and lan_netmask):
            return

        try:
            lan_netmask_bits = get_netmask_bits(lan_netmask)

        except:
            print("Invalid netmask %r, skipping" % lan_netmask)
            return

        print(nmcli(
            'connection', 'add',
            'ifname', 'lan',
            'type', 'bridge',
            'con-name', 'lan',
            'ip4', '{}/{}'.format(lan_address, lan_netmask_bits),
        ))
        print(nmcli(
            'connection', 'modify',
            'lan',
            'bridge.stp', 'no',
        ))

        bridge_interfaces['lan'] = {}

    if liquid_lan.get('eth'):
        if ETHERNET_INTERFACE not in bridge_interfaces['lan']:
            print(nmcli(
                'connection', 'add',
                'type', 'bridge-slave',
                'ifname', ETHERNET_INTERFACE,
                'master', 'lan',
            ))

    else:
        uuid = bridge_interfaces['lan'].get(ETHERNET_INTERFACE)
        if uuid:
            print(nmcli('connection', 'del', uuid))
