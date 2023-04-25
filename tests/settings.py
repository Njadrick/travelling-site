DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db'
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'kanisa.middleware.KanisaPageFallbackMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'kanisa.context_processors.kanisa_settings',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    'sorl.thumbnail',
    'crispy_forms',
    'haystack',
    'mptt',
    'recurrence',
    'kanisa',
)

LOGIN_URL = '/members/account/login/'

ROOT_URLCONF = 'tests.tox.urls'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)

import os
PROJECT_DIR = os.path.dirname(__file__)
j = lambda filename: os.path.join(PROJECT_DIR, filename)

HAYSTACK_SITECONF = 'tests.tox.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = j('.test_whoosh')

DATE_FORMAT = 'N j, Y'
TIME_FORMAT = 'P'
SHORT_DATE_FORMAT = 'm/d/Y'

STATIC_URL = '/fakestatictrees/'

TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap'

AUTH_USER_MODEL = 'kanisa.RegisteredUser'

SECRET_KEY = 'thisbagismadefromrecycledmaterial'
