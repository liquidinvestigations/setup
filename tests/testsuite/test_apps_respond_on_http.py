import os
import pytest
import requests

DOMAIN = 'liquid.example.org'
SUBDOMAINS = [
    'hoover',
    'hypothesis',
    'client.hypothesis',
    'matrix',
    'dokuwiki',
    'davros',
]
if os.environ.get('NOAPPS'):
    SUBDOMAINS = []
FQDN_LIST = [DOMAIN] + [sub + '.' + DOMAIN for sub in SUBDOMAINS]
URLS = ['http://' + fqdn for fqdn in FQDN_LIST]

# TODO list app ports on localhost and test if they're reachable

@pytest.mark.parametrize('url',URLS)
def test_app_url_reachable(url):
    get = requests.get(url)
    assert get.status_code == 200
