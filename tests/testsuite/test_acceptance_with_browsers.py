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


@pytest.fixture(params=['firefox', 'chrome'])
def browser(request):
    browser_name = request.param
    with splinter.Browser(browser_name, headless=True, wait_time=10, **BROWSER_OPTS[browser_name]) as browser:
        browser.driver.set_window_size(1920, 1080)
        browser.visit(URL)
        yield browser


@pytest.mark.parametrize('browser', ['firefox'], indirect=True)
def test_browser_welcome(browser):
    assert browser.url.endswith('/welcome/')
    assert browser.is_element_present_by_text("Liquid Investigations")
    assert browser.is_text_present("Congratulations")
    
    browser.fill('admin-username', ADMIN_USERNAME)
    browser.fill('admin-password', ADMIN_PASSWORD)
    browser.fill('hotspot-ssid', HOTSPOT_SSID)
    browser.fill('hotspot-password', HOTSPOT_PASSWORD)
    
    browser.find_by_text('Apply').click()

    assert browser.is_element_present_by_text("Liquid Investigations")
    assert browser.is_text_present("Your settings are being applied")
    assert browser.is_text_present("Wait a minute")

    browser.visit(URL)
    assert not browser.url.endswith('/welcome/')


def test_view_home_page(browser):
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")

    for app_name in APP_NAMES:
        assert browser.is_text_present(app_name)


def test_login_into_home_page(browser):
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")

    # login
    browser.find_by_text('[login]').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()
    
    # check that we're logged in
    assert browser.is_element_present_by_text("Liquid Investigations")
    assert browser.is_text_present("[admin]")
    assert browser.is_text_present("[logout]")
    assert browser.is_text_present(ADMIN_USERNAME)

    # logout
    browser.find_by_text('[logout]').click()
    assert browser.is_element_present_by_text("[login]")
    assert not browser.is_text_present(ADMIN_USERNAME)


def test_login_into_dokuwiki(browser):
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")
    
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
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")
    
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
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")
    
    # navigate to matrix and login
    browser.find_by_text('Matrix').click()
    assert browser.is_element_present_by_text("Matrix ID (e.g. @bob:matrix.org or bob)")
    browser.find_by_css('#user_id').fill(ADMIN_USERNAME)
    browser.find_by_css('#password').fill(ADMIN_PASSWORD)
    browser.find_by_css('button#login').click()

    # we should be logged in now, let's check
    assert browser.is_element_present_by_text(ADMIN_USERNAME)
    assert browser.is_text_present("Welcome to homeserver")
    assert browser.is_text_present("Log out")

    browser.find_by_text('Log out').click()
    assert browser.is_element_present_by_text("Matrix ID (e.g. @bob:matrix.org or bob)")


def test_login_into_davros(browser):
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")
    
    # navigate to davros and login
    browser.find_by_text('Davros').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()

    assert browser.is_element_present_by_text("Updated")
    assert browser.is_text_present("Files in home")
    assert browser.is_text_present(".gitkeep")


def test_login_into_hoover(browser):
    skip_if_welcome_not_set(browser)
    assert browser.is_element_present_by_text("Liquid Investigations")

    # login
    browser.find_by_text('[login]').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()
    
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
    skip_if_welcome_not_set(browser)

    # login
    browser.find_by_text('[login]').click()
    browser.fill('username', ADMIN_USERNAME)
    browser.fill('password', ADMIN_PASSWORD)
    browser.find_by_text('login').click()
    browser.find_by_text('[admin]').click()


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
    #assert browser.is_text_present(HOTSPOT_SSID)
    #assert browser.is_text_present(HOTSPOT_PASSWORD)
    assert browser.is_text_present('DHCP Range')
    assert browser.is_text_present('Netmask')


def test_admin_network_wan_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/network')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/network/wan')

    assert browser.is_text_present('DHCP')
    #assert browser.is_text_present('Gateway')
    assert browser.is_text_present('DNS Server')


def test_admin_network_ssh_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/network')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/network/ssh')

    assert browser.is_element_present_by_text('SSH')
    #assert browser.is_text_present('Port')


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
    #assert browser.is_text_present("Enable VPN server")
    assert browser.is_text_present("Generate new key")
    assert browser.is_text_present("Active keys")


def test_admin_vpn_client_tab(browser):
    navigate_to_admin(browser)
    browser.click_link_by_href('/admin-ui/vpn')
    assert browser.is_element_not_present_by_css('div.loading')
    browser.click_link_by_href('/admin-ui/vpn/client')
    #assert browser.is_text_present("Enable VPN client")
    #assert browser.is_text_present("Upload key")


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

    assert browser.is_text_present("Lorem ipsum dolor sit amet")

