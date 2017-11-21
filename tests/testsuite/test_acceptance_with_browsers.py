import time
import requests
import splinter
import pytest
from selenium.webdriver.chrome.options import Options as ChromeOptions

DOMAIN = 'liquid.example.org'
URL = 'http://'+DOMAIN

ADMIN_USERNAME = 'testadmin'
ADMIN_PASSWORD = 'test-liquid.example.org'
HOTSPOT_SSID = 'testhotspotssid'
HOTSPOT_PASSWORD = 'testhotspotpassword'

APP_NAMES = [
    "Hoover",
    "Hypothesis",
    "DokuWiki",
    "Matrix",
    "Davros",
]

BROWSERS = [
    'firefox',
    'chrome',
]

chrome_options = ChromeOptions()
chrome_options.add_argument('--no-sandbox')

BROWSER_OPTS = {
    'firefox': {
    },
    'chrome': {
        'service_args': ['--verbose', '--log-path=chromedriver.log'],
        'options': chrome_options,
    },
}


def skip_if_welcome_not_set(browser):
    browser.visit(URL)
    if browser.url.endswith('/welcome/'):
        pytest.skip('welcome not done, skipping')


def wait_for_reconfigure():
    LOGIN_URL = URL + "/accounts/login/"
    client = requests.session()
    r = client.get(LOGIN_URL)
    assert r.status_code == 200
    csrftoken = client.cookies['csrftoken']

    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'csrfmiddlewaretoken': csrftoken,
        'next': '/',
    }

    r = client.post(LOGIN_URL, data=login_data, headers={'Referer': LOGIN_URL})
    assert r.status_code == 200

    RECONFIGURE_URL = URL + "/api/configure/status/"

    WAIT_TIME = 3 * 60
    WAIT_INCREMENT = 3

    t0 = time.time()
    while time.time() < t0 + WAIT_TIME:
        time.sleep(WAIT_INCREMENT)
        try:
            r = client.get(RECONFIGURE_URL)
        except requests.exceptions.ConnectionError:
            # retry on connection errors (because nginx or django is being restarted)
            continue

        if r.status_code >= 500:
            # retry on internal errors
            continue

        assert r.status_code == 200
        status = r.json()['status']

        if status == 'ok':
            return
        elif status == 'broken':
            pytest.fail("{} returned broken!".format(RECONFIGURE_URL))
        elif status == 'configuring':
            # wait some more for it
            continue
        else:
            pytest.fail("{} returned unknown value for status: {}".format(RECONFIGURE_URL, status))

    pytest.fail("{} timed out".format(RECONFIGURE_URL))


@pytest.fixture(params=BROWSERS)
def browser(request):
    browser_name = request.param
    with splinter.Browser(browser_name, headless=True, wait_time=10, **BROWSER_OPTS[browser_name]) as browser:
        browser.driver.set_window_size(1920, 1080)
        browser.visit(URL)
        yield browser


@pytest.mark.parametrize('browser', [BROWSERS[0]], indirect=True)
def test_browser_welcome(browser):
    assert browser.url.endswith('/welcome/')
    assert browser.is_element_present_by_text("Welcome!")
    assert browser.is_text_present("Congratulations")

    browser.fill('admin-username', ADMIN_USERNAME)
    browser.fill('admin-password', ADMIN_PASSWORD)
    browser.fill('hotspot-ssid', HOTSPOT_SSID)
    browser.fill('hotspot-password', HOTSPOT_PASSWORD)

    browser.find_by_css('button[type=submit]').click()

    assert browser.is_element_present_by_text("Welcome!")
    assert browser.is_text_present("Your settings are being applied")
    assert browser.is_text_present("Wait a minute")

    wait_for_reconfigure()

    browser.visit(URL)
    assert not browser.url.endswith('/welcome/')

def login_admin_into_homepage(browser):
    skip_if_welcome_not_set(browser)

    browser.visit(URL)
    assert browser.url.endswith('/accounts/login/')
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_css('button[type=submit]').click()

    assert browser.is_element_present_by_text("Hello {}!".format(ADMIN_USERNAME))


def test_view_home_page(browser):
    login_admin_into_homepage(browser)

    for app_name in APP_NAMES:
        assert browser.is_text_present(app_name.upper())


def test_login_into_home_page(browser):
    login_admin_into_homepage(browser)

    assert browser.is_text_present("Admin")
    assert browser.is_text_present("Django Admin")
    assert browser.is_text_present("Reconfigure")
    assert browser.is_text_present(ADMIN_USERNAME)

    # logout
    with browser.get_iframe('liMenu') as menu:
        menu.click_link_by_partial_href("/accounts/logout/")

    assert browser.url.endswith('/accounts/login/')


def test_login_into_dokuwiki(browser):
    login_admin_into_homepage(browser)

    # navigate to dokuwiki and login
    browser.find_by_text('DokuWiki').click()
    assert browser.is_element_present_by_text("Permission Denied")
    browser.fill('u', ADMIN_USERNAME)
    browser.fill('p', ADMIN_PASSWORD)
    browser.find_by_css('#dw__login button[type=submit]').click()

    # we should be logged in now, let's check
    assert browser.is_element_present_by_text(ADMIN_USERNAME)
    assert browser.is_text_present("Admin")
    assert browser.is_text_present("Log Out")

    browser.find_by_text('Log Out').click()
    assert browser.is_element_present_by_text("Permission Denied")


def test_login_into_hypothesis(browser):
    login_admin_into_homepage(browser)

    # navigate to hypothesis and login
    browser.find_by_text('Hypothesis').click()
    browser.find_by_text('Log in').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_css('#deformLog_in').click()

    # we should be logged in now, let's check
    assert browser.is_element_present_by_text(ADMIN_USERNAME)
    assert browser.is_text_present("How to get started")


def test_login_into_matrix(browser):
    login_admin_into_homepage(browser)

    # navigate to matrix and login
    browser.find_by_text('Matrix').click()
    assert browser.is_element_present_by_text("Matrix ID (e.g. @bob:matrix.org or bob)")
    browser.find_by_css('#user_id').fill(ADMIN_USERNAME)
    browser.find_by_css('#password').fill(ADMIN_PASSWORD)
    browser.find_by_css('button#login').click()

    # we should be logged in now, let's check
    assert browser.is_element_present_by_text(ADMIN_USERNAME)
    assert browser.is_text_present("Welcome to homeserver")


def test_login_into_davros(browser):
    login_admin_into_homepage(browser)

    # navigate to davros and login
    browser.find_by_text('Davros').click()

    assert browser.is_element_present_by_text("Updated")
    assert browser.is_text_present("Files in home")
    assert browser.is_text_present(".gitkeep")


def test_login_into_hoover(browser):
    login_admin_into_homepage(browser)

    # navigate to hoover
    browser.find_by_text('Hoover').click()

    # click on the menu and on "login"
    browser.find_by_id('loggedin-btngroup').click()
    assert browser.is_element_present_by_text("login")
    browser.find_by_text('login').click()

    # we should be logged in because oauth
    browser.find_by_id('loggedin-btngroup').click()
    assert browser.is_element_present_by_text("admin")
    assert browser.is_text_present("change password")
    assert browser.is_text_present("({}) logout".format(ADMIN_USERNAME))

    # let's wander around the hoover django admin
    browser.find_by_text('admin').click()
    assert browser.is_element_present_by_text("Site administration")
    assert browser.is_text_present("LOG OUT")

    # let's log out from the django admin
    browser.find_by_text('Log out').click()

    # and check that we're logged out
    browser.find_by_id('loggedin-btngroup').click()
    assert browser.is_element_present_by_text("login")


def navigate_to_admin(browser):
    login_admin_into_homepage(browser)

    # login
    browser.find_by_text('Admin').click()


def test_admin_header_and_redirect_to_status(browser):
    navigate_to_admin(browser)

    assert browser.is_text_present("admin")
    assert browser.is_text_present("Logged in as: {}".format(ADMIN_USERNAME))


def test_admin_general_status_tab(browser):
    navigate_to_admin(browser)
    assert browser.url.endswith("/admin-ui/status")
    browser.click_link_by_href('/admin-ui/status')

    assert browser.url.endswith("/admin-ui/status")
    assert browser.is_text_present("General Status")


def test_admin_network_status_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/network')
    assert browser.url.endswith('/admin-ui/network/status')

    assert browser.is_element_present_by_text("Network Configuration")
    assert browser.is_text_present("Domain")
    assert browser.is_text_present(DOMAIN)
    assert browser.is_text_present("Lan configuration")
    assert browser.is_text_present(HOTSPOT_SSID)


def test_admin_network_lan_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/network')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/network/lan')

    # TODO test these; they don't show up as text because they're inside inputs
    # assert browser.is_text_present(HOTSPOT_SSID)
    # assert browser.is_text_present(HOTSPOT_PASSWORD)
    assert browser.is_text_present('DHCP Range')
    assert browser.is_text_present('Netmask')


def test_admin_network_wan_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/network')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/network/wan')

    assert browser.is_text_present('DHCP')
    # assert browser.is_text_present('Gateway')
    assert browser.is_text_present('DNS Server')


def test_admin_network_ssh_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/network')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/network/ssh')

    assert browser.is_element_present_by_text('SSH')
    # assert browser.is_text_present('Port')


def test_admin_vpn_status_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/vpn')
    assert browser.url.endswith('/admin-ui/vpn/status')

    assert browser.is_element_present_by_text("VPN Configuration")
    assert browser.is_text_present("Server configuration")
    assert browser.is_text_present("Client configuration")
    assert browser.is_text_present("Connection count")


def test_admin_vpn_server_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/vpn')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/vpn/server')
    # assert browser.is_text_present("Enable VPN server")
    assert browser.is_text_present("Generate new key")
    assert browser.is_text_present("Active keys")


def test_admin_vpn_client_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/vpn')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/vpn/client')
    # assert browser.is_text_present("Enable VPN client")
    # assert browser.is_text_present("Upload key")


def test_admin_services_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/services')
    assert browser.is_element_not_present_by_css('div.loading')
    assert browser.is_text_present("Services")
    for app_name in APP_NAMES:
        assert browser.is_text_present(app_name.upper())
    for app_desc in ['Search Tool', 'Annotations', 'Chat', 'Wiki', 'File Sharing']:
        assert browser.is_text_present(app_desc)


def test_admin_users_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/users')

    assert browser.is_element_present_by_text("Users")
    assert browser.is_text_present("Active users")
    assert browser.is_text_present("Inactive users")


def test_admin_discovery_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/discovery')

    assert browser.is_element_present_by_text("Discovery")
    assert browser.is_text_present("Trusted nodes")
    assert browser.is_text_present("Untrusted nodes")


def test_admin_about_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/about')

    assert browser.is_text_present("The Liquid investigations project")
    assert browser.is_text_present("Romanian Centre for Investigative Journalism")
    assert browser.is_text_present("you can contact our development and support team")
