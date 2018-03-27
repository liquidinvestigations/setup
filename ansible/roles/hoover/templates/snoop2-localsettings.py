from .defaultsettings import *
from .secret_key import SECRET_KEY

DEBUG = {% if devel %}True{% else %}False{% endif %}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hoover-snoop2',
    }
}

ALLOWED_HOSTS = ["localhost"]

SNOOP_TIKA_URL = 'http://localhost:15423'

SNOOP_BLOB_STORAGE = '/var/lib/liquid/hoover/blobs'

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672/snoop2'
