import requests

def test_google_reachable():
    google = requests.get('https://google.com')
    assert google.status_code == 200
    assert 'google' in google.text
