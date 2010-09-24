# -*- coding: utf-8 -*-
import local

DEBUG = getattr(local, 'DEBUG', False)
DEBUG_TOOLBAR = getattr(local, 'DEBUG_TOOLBAR', False)
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Operational Team', 'ops@e-loue.com'),
)

MANAGERS = ADMINS

# Email configuration
SERVER_EMAIL = 'noreply@e-loue.com'
DEFAULT_FROM_EMAIL = 'noreply@e-loue.com'

DATABASES = {
    'default':{
        'NAME':getattr(local, 'DATABASE_NAME', '../eloue.db'),
        'ENGINE':getattr(local, 'DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'USER':getattr(local, 'DATABASE_USER', ''),
        'PASSWORD':getattr(local, 'DATABASE_PASSWORD', ''),
        'HOST':getattr(local, 'DATABASE_HOST', ''),
        'PORT':getattr(local, 'DATABASE_PORT', ''),
        'OPTIONS':getattr(local, 'DATABASE_OPTIONS', {})
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = local.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = local.MEDIA_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0j7jp$u!5n00s7=e@evlo0%ng&xm%zv^3-vn6gyy$&nbdd7p*('

# List of callables that know how to import templates from various sources.
if not DEBUG:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
            )
        ),
    )
else:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
)
if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'eloue.urls'

TEMPLATE_DIRS = getattr(local, 'TEMPLATE_DIRS')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sitemaps',
    'django.contrib.formtools',
    'django.contrib.markup',
    'django.contrib.gis',
    'south',
    'django_lean.experiments',
    'compress',
    'announcements',
    'haystack',
    'django_nose',
    'eloue.accounts',
    'eloue.rent',
    'eloue.products',
    'eloue.quack'
)

# Authentification configuration
AUTHENTICATION_BACKENDS = (
    'eloue.accounts.auth.PatronModelBackend',
)
ACCOUNT_ACTIVATION_DAYS = 7

# Tests configuration
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = getattr(local, 'NOSE_ARGS', ['--stop', '--with-doctest', '--cover-package=eloue', '--with-freshen', '--cover-branches'])
NOSE_PLUGINS = getattr(local, 'NOSE_PLUGINS', [])

# Message configuration
MESSAGE_STORAGE = getattr(local, 'MESSAGE_STORAGE', 'django.contrib.messages.storage.session.SessionStorage')

# Session configuration
SESSION_ENGINE = local.SESSION_ENGINE
SESSION_COOKIE_DOMAIN = local.SESSION_COOKIE_DOMAIN

# Cache configuration
CACHE_BACKEND = local.CACHE_BACKEND
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 60 * 15
CACHE_MIDDLEWARE_KEY_PREFIX = getattr(local, 'CACHE_MIDDLEWARE_KEY_PREFIX', None)

# Compress configuration
COMPRESS = getattr(local, 'COMPRESS', True)
COMPRESS_VERSION = True
COMPRESS_JS_FILTERS = getattr(local, 'COMPRESS_JS_FILTERS', None)
COMPRESS_CSS_FILTERS = getattr(local, 'COMPRESS_CSS_FILTERS', None)
COMPRESS_CLOSURE_BINARY = getattr(local, 'COMPRESS_CLOSURE_BINARY', 'java -jar compiler.jar')
CSSTIDY_ARGUMENTS = '--template=highest'

# South configuration
SOUTH_TESTS_MIGRATE = getattr(local, 'SOUTH_TESTS_MIGRATE', True)

# Haystack configuration
HAYSTACK_SITECONF = 'eloue.sites'
HAYSTACK_SEARCH_ENGINE = getattr(local, 'HAYSTACK_SEARCH_ENGINE', 'solr')
HAYSTACK_SOLR_URL = getattr(local, 'HAYSTACK_SOLR_URL', 'http://localhost:8983/solr')
HAYSTACK_INCLUDE_SPELLING = True
HAYSTACK_ENABLE_REGISTRATIONS = True

# Logging configuration
try:
    from logbook.more import ColorizedStderrHandler
    handler = ColorizedStderrHandler()
    handler.push_application()
except ImportError:
    pass

# Lean configuration
LEAN_ENGAGEMENT_CALCULATOR = 'eloue.lean.PatronEngagementScoreCalculator'

# Geocoding API
GOOGLE_API_KEY = 'ABQIAAAA7bPNcG5t1-bTyW9iNmI-jRRqVDjnV4vohYMgEqqi0RF2UFYT-xSSwfcv2yfC-sACkmL4FuG-A_bScQ'
YAHOO_API_KEY = 'nnZZkyvV34Fkk9DOWOpYJL7C41.ispEvSVAXbA3Dhu894gljv877.G6KewexGZKhs7S6dSwxCvM-'

# SSL configuration
USE_HTTPS = getattr(local, 'USE_HTTPS', True)
SESSION_COOKIE_SECURE = getattr(local, 'SESSION_COOKIE_SECURE', True)

# S3 configuration
AWS_ACCESS_KEY_ID = getattr(local, 'AWS_ACCESS_KEY_ID', 'AKIAJ3PXVVKSTM3WSZSQ')
AWS_SECRET_ACCESS_KEY = getattr(local, 'AWS_SECRET_ACCESS_KEY', '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')
AWS_STORAGE_BUCKET_NAME = getattr(local, 'AWS_STORAGE_BUCKET_NAME', 'eloue')
AWS_S3_CUSTOM_DOMAIN = getattr(local, 'AWS_S3_CUSTOM_DOMAIN', '')
AWS_DEFAULT_ACL = getattr(local, 'AWS_DEFAULT_ACL', 'public-read')
AWS_LOCATION = getattr(local, 'AWS_LOCATION', 'EU')
AWS_AUTO_CREATE_BUCKET = getattr(local, 'AWS_AUTO_CREATE_BUCKET', False)

# Paypal configuration
USE_PAYPAL_SANDBOX = getattr(local, 'USE_PAYPAL_SANDBOX', DEBUG)
VALIDATE_IPN = getattr(local, 'VALIDATE_IPN', True)
PAYPAL_MERCHANT_REFERRAL = "Z6GVNB75VNCTU"
if USE_PAYPAL_SANDBOX:
    PAYPAL_API_USERNAME = getattr(local, 'PAYPAL_SANDBOX_API_USERNAME', "sand_1266353156_biz_api1.tryphon.org")
    PAYPAL_API_PASSWORD = getattr(local, 'PAYPAL_SANDBOX_API_PASSWORD', "1266353174")
    PAYPAL_API_SIGNATURE = getattr(local, 'PAYPAL_SANDBOX_API_SIGNATURE', "ACFP1tIskAXJ.m25BMGIQFW.gpwvAQpVs6wPW462vdrnRb5OjB-r5Jsu")
    PAYPAL_API_APPLICATION_ID = getattr(local, 'PAYPAL_SANDBOX_API_APPLICATION_ID', 'APP-80W284485P519543T')
    PAYPAL_API_EMAIL = getattr(local, 'PAYPAL_API_EMAIL', 'sand_1266353156_biz@tryphon.org')
else:
    PAYPAL_API_USERNAME = getattr(local, 'PAYPAL_API_USERNAME')
    PAYPAL_API_PASSWORD = getattr(local, 'PAYPAL_API_PASSWORD')
    PAYPAL_API_SIGNATURE = getattr(local, 'PAYPAL_API_SIGNATURE')
    PAYPAL_API_APPLICATION_ID = getattr(local, 'PAYPAL_API_APPLICATION_ID')
    PAYPAL_API_EMAIL = getattr(local, 'PAYPAL_API_EMAIL')

# Business configuration
BOOKING_DAYS = 85 # Max booking days
FEE_PERCENTAGE = 0.1 # Our commission percentage
POLICY_NUMBER = None # Our insurance policy number
PARTNER_NUMBER = None # Our insurance partner number
INSURANCE_FTP_HOST = None # Our insurance ftp server host
INSURANCE_FTP_USER = None # Our insurance ftp server username
INSURANCE_FTP_PASSWORD = None # Our insurance ftp server password
INSURANCE_FTP_CWD = None # Our insurance ftp server directory
