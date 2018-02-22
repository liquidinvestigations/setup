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
