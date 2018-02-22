import os.path
import re

DEBUG = {% if devel %}True{% else %}False{% endif %}

ALLOWED_HOSTS = ['{{ liquid_domain }}']
AUTH_PASSWORD_VALIDATORS = []

CORS_ORIGIN_REGEX_WHITELIST = [
    '^(https?://)?(\w+\.)?' + re.escape('{{ liquid_domain }}') + r'$',
]
CORS_ALLOW_CREDENTIALS = True

INVOKE_HOOK = 'sudo /opt/common/libexec/invoke-hook'

{% if liquid_services.hoover.enabled %}
HOOVER_APP_URL = 'http://hoover.{{ liquid_domain }}'
{% endif %}

{% if liquid_services.hypothesis.enabled %}
HYPOTHESIS_APP_URL = 'http://hypothesis.{{ liquid_domain }}'
{% endif %}

{% if liquid_services.dokuwiki.enabled %}
DOKUWIKI_APP_URL = 'http://dokuwiki.{{ liquid_domain }}'
{% endif %}

{% if liquid_services.matrix.enabled %}
MATRIX_APP_URL = 'http://riot.{{ liquid_domain }}'
{% endif %}

{% if liquid_services.davros.enabled %}
DAVROS_APP_URL = 'http://davros.{{ liquid_domain }}'
{% endif %}

LIQUID_DOMAIN = '{{ liquid_domain }}'

DISCOVERY_URL = 'http://localhost:13777'

LIQUID_SETUP_RECONFIGURE = 'sudo /opt/setup/libexec/liquid-core-reconfigure'
LIQUID_CORE_VAR = '/var/lib/liquid/core'
LIQUID_SUPERVISORCTL = 'sudo /usr/bin/supervisorctl'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(LIQUID_CORE_VAR, 'db.sqlite3'),
    }
}

from .secret_key import SECRET_KEY
