SECRET_KEY = '-- secret key --'
DEBUG = True
ALLOWED_HOSTS = ['{{ domain }}']
AUTH_PASSWORD_VALIDATORS = []
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/liquid-core/var/db.sqlite3',
    }
}
