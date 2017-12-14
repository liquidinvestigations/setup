import re
import subprocess


def nmcli(*args):
    cmd = ['nmcli'] + list(args)
    print('+', ' '.join(cmd))
    return subprocess.check_output(cmd).decode('latin1')


def iter_nmcli_output(output, field_names):
    for line in output.splitlines():
        yield dict(zip(field_names, line.split(':')))


def get_devices():
    fields = ['device', 'type']
    out = nmcli('-t', '-f', ','.join(fields), 'dev')
    return iter_nmcli_output(out, fields)


def get_connections():
    fields = ['uuid', 'type', 'device', 'name']
    out = nmcli('-t', '-f', ','.join(fields), 'con')
    return iter_nmcli_output(out, fields)


def get_connection_properties(uuid):
    properties = {}
    for line in nmcli('con', 'show', '--show-secrets', uuid).splitlines():
        m = re.match(r'^(?P<key>[^:]+):\s+(?P<value>.*)$', line.strip())
        if not m:
            continue
        properties[m.group('key')] = m.group('value')

    return properties
