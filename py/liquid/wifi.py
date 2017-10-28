import re
import subprocess


def nmcli(*args):
    cmd = ['nmcli'] + list(args)
    print('+', ' '.join(cmd))
    return subprocess.check_output(cmd).decode('latin1')


def get_wifi_devices():
    for line in nmcli('-t', '-f', 'device,type', 'dev').splitlines():
        (device, type) = line.split(':')
        if type == 'wifi':
            yield device


def get_wifi_cons():
    for line in nmcli('-t', '-f', 'uuid,type,device,name', 'con').splitlines():
        (uuid, type, device, name) = line.split(':')
        if type == '802-11-wireless':
            yield uuid, device


def get_con_properties(uuid):
    properties = {}
    for line in nmcli('con', 'show', '--show-secrets', uuid).splitlines():
        m = re.match(r'^(?P<key>[^:]+):\s+(?P<value>.*)$', line.strip())
        if not m:
            continue
        properties[m.group('key')] = m.group('value')

    return properties


def delete_connection(uuid):
    print(nmcli('con', 'del', uuid))


def configure_wifi(vars):
    def not_empty(wifi_config):
        if wifi_config:
            if wifi_config['ssid'] and wifi_config['password']:
                return wifi_config
        return None

    print('vars:', vars)
    target = {
        'hotspot': not_empty(vars.get('liquidcore_lan', {}).get('hotspot')),
        'client': not_empty(vars.get('liquidcore_wan', {}).get('wifi')),
    }
    print('target:', target)

    wifi_devices = set(get_wifi_devices())
    print('wifi devices:', wifi_devices)

    for uuid, device in get_wifi_cons():
        device_is_present = device in wifi_devices
        print('device is present?', device, device_is_present)
        if not device_is_present:
            print('deleting connection', uuid)
            delete_connection(uuid)
            continue

        properties = get_con_properties(uuid)

        if properties['802-11-wireless.mode'] == 'ap':
            print('found a hotspot:', device, uuid)

            if target.get('hotspot'):
                # let's see if the hotspot is configured as we like
                ssid_ok = (properties['802-11-wireless.ssid'] == target['hotspot']['ssid'])
                psk_ok = (properties['802-11-wireless-security.psk'] == target['hotspot']['password'])
                autoconnect_ok = (properties['connection.autoconnect'] == 'yes')
                print('checking if hotspot configuration is good ...')
                print('ssid_ok:', ssid_ok)
                print('psk_ok:', psk_ok)
                print('autoconnect_ok:', autoconnect_ok)
                if ssid_ok and psk_ok and autoconnect_ok:
                    # yep, it's ok, remove it from our target, and device list, and move on
                    del target['hotspot']
                    wifi_devices.remove(device)
                    continue
                # nope, we'll delete it

        if properties['802-11-wireless.mode'] == 'infrastructure':
            print('found a client:', device, uuid)

            if target.get('client'):
                # let's see if the client is configured as we like
                ssid_ok = (properties['802-11-wireless.ssid'] == target['client']['ssid'])
                psk_ok = (properties['802-11-wireless-security.psk'] == target['client']['password'])
                print('checking if client configuration is good ...')
                print('ssid_ok:', ssid_ok)
                print('psk_ok:', psk_ok)
                if ssid_ok and psk_ok:
                    # yep, it's ok, remove it from our target, and device list, and move on
                    del target['client']
                    wifi_devices.remove(device)
                    continue
                # nope, we'll delete it

        # we don't need this wifi connection, delete it
        print('deleting connection', uuid)
        delete_connection(uuid)

    if target.get('hotspot'):
        if wifi_devices:
            device = wifi_devices.pop()
            print('creating wifi hotspot')
            print(nmcli(
                'device', 'wifi',
                'hotspot', 'ssid', target['hotspot']['ssid'],
                'password', target['hotspot']['password'],
                'ifname', device,
                'con-name', 'liquid-hotspot',
            ))
            print(nmcli(
                'connection', 'modify', 'liquid-hotspot',
                'connection.autoconnect', 'yes',
            ))

        else:
            print('no wifi device available to use as hotspot')

    if target.get('client'):
        if wifi_devices:
            device = wifi_devices.pop()
            print('creating wifi client')
            print(nmcli(
                'device', 'wifi',
                'connect', target['client']['ssid'],
                'password', target['client']['password'],
                'ifname', device,
                'name', 'liquid-client',
            ))

        else:
            print('no wifi device available to use as client')
