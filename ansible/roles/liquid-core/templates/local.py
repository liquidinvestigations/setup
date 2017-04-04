SECRET_KEY = '-- secret key --'
DEBUG = True
ALLOWED_HOSTS = ['{{ liquid_domain }}']
AUTH_PASSWORD_VALIDATORS = []
CORS_ORIGIN_ALLOW_ALL = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/liquid-core/var/db.sqlite3',
    }
}

HYPOTHESIS_CREATE_USER_SCRIPT = '/opt/liquid-core/libexec/create_h_user'
