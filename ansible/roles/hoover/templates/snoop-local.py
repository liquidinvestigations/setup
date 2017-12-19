DEBUG = {% if devel %}True{% else %}False{% endif %}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hoover-snoop',
    }
}

ALLOWED_HOSTS = ["localhost"]

SNOOP_ELASTICSEARCH_URL = 'http://localhost:14352'
SNOOP_TIKA_SERVER_ENDPOINT = 'http://localhost:15423'

SNOOP_ARCHIVE_CACHE_ROOT = '/opt/hoover/cache/archives'
SNOOP_SEVENZIP_BINARY = '/usr/bin/7z'

SNOOP_MSG_CACHE = '/opt/hoover/cache/msg'
SNOOP_MSGCONVERT_SCRIPT = '/usr/local/bin/msgconvert'

SNOOP_PST_CACHE_ROOT = '/opt/hoover/cache/pst'
SNOOP_READPST_BINARY = '/usr/bin/readpst'

SNOOP_GPG_HOME = '/opt/hoover/cache/gpg_home'
SNOOP_GPG_BINARY = '/usr/bin/gpg'

from .secret_key import SECRET_KEY
