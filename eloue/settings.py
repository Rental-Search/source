# -*- coding: utf-8 -*-
import local
import logging

DEBUG = getattr(local, 'DEBUG', False)
DEBUG_TOOLBAR = getattr(local, 'DEBUG_TOOLBAR', False)
TEMPLATE_DEBUG = DEBUG

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

ADMINS = (
    ('Operational Team', 'ops@e-loue.com'),
)

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

# Email configuration
SERVER_EMAIL = 'contact@e-loue.com'
DEFAULT_FROM_EMAIL = 'contact@e-loue.com'

EMAIL_HOST = getattr(local, 'EMAIL_HOST', 'smtp.postmarkapp.com')
EMAIL_USE_TLS = getattr(local, 'EMAIL_USE_TLS', True)
EMAIL_PORT = getattr(local, 'EMAIL_PORT', 2525)
EMAIL_HOST_USER = getattr(local, 'EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = getattr(local, 'EMAIL_HOST_PASSWORD', '')

DATABASES = {
    'default': {
        'NAME': getattr(local, 'DATABASE_NAME', 'eloue'),
        'ENGINE': getattr(local, 'DATABASE_ENGINE', 'django.contrib.gis.db.backends.postgis'),
        'USER': getattr(local, 'DATABASE_USER', 'eloue'),
        'PASSWORD': getattr(local, 'DATABASE_PASSWORD', ''),
        'HOST': getattr(local, 'DATABASE_HOST', ''),
        'PORT': getattr(local, 'DATABASE_PORT', ''),
        'OPTIONS': getattr(local, 'DATABASE_OPTIONS', {'autocommit': True})
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
LANGUAGE_CODE = 'fr-fr'

ugettext = lambda s: s
LANGUAGES = (
    ('fr-fr', ugettext('Français')),
    ('en-gb', ugettext('English')),
)

SITE_ID = 1
DEFAULT_SITES = getattr(local, "DEFAULT_SITES", [1, 2, 3])

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
FORMAT_MODULE_PATH = 'eloue.formats'

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
    'announcements.context_processors.site_wide_announcements',
    'django_messages.context_processors.inbox',
    'eloue.context_processors.site',
    'eloue.context_processors.debug',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'eloue.middleware.SpacelessMiddleware',
    'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# Urls configuration
ROOT_URLCONF = 'eloue.urls'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/dashboard/'

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
    'mptt',
    'imagekit',
    'django_lean.experiments',
    'rollout',
    'compress',
    'faq',
    'announcements',
    'haystack',
    'queued_search',
    'django_nose',
    'accounts',
    'rent',
    'django_messages',
    'products',
    'api',
    'oauth_provider',
)
if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)

LOCAL_APPS = getattr(local, 'INSTALLED_APPS', None)
if LOCAL_APPS:
    INSTALLED_APPS += LOCAL_APPS


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
CACHE_MIDDLEWARE_SECONDS = getattr(local, 'CACHE_MIDDLEWARE_SECONDS', 60 * 15)
CACHE_MIDDLEWARE_KEY_PREFIX = getattr(local, 'CACHE_MIDDLEWARE_KEY_PREFIX', None)

# Compress configuration
COMPRESS = getattr(local, 'COMPRESS', True)
COMPRESS_AUTO = getattr(local, 'COMPRESS_AUTO', False)
COMPRESS_VERSION_REMOVE_OLD = False
COMPRESS_VERSION = True
COMPRESS_CSS_URL_REPLACE = {
    r"\.\.\/": "",
    r"url\([\'|\"]([^(|\'|\"|\)]*)[\'|\"|\)]+": lambda m: "url(\"%s%s\")" % (MEDIA_URL, m.group(1)) if not m.group(1).startswith("http") else "url(\"%s\")" % m.group(1),
    r"src=[\'|\"]([^(\'|\")]*)[\'|\"]": lambda m: "src=\"%s%s\"" % (MEDIA_URL, m.group(1)),
}
COMPRESS_JS_FILTERS = getattr(local, 'COMPRESS_JS_FILTERS', ('compress.filters.yui.YUICompressorFilter',))
COMPRESS_CSS_FILTERS = getattr(local, 'COMPRESS_CSS_FILTERS', (
    'compress.filters.css_url_replace.CSSURLReplace',
    'compress.filters.yui.YUICompressorFilter'
))
COMPRESS_YUI_BINARY = getattr(local, 'COMPRESS_YUI_BINARY', '/usr/bin/yui-compressor')
COMPRESS_CSS = {
    'master': {
        'source_filenames': (
            'css/screen.css',
            'css/custom.css',
            'css/plugins/ui/jquery.ui.core.css',
            'css/plugins/ui/jquery.ui.datepicker.css',
            'css/plugins/ui/jquery.ui.tabs.css',
            'css/plugins/ui/jquery.ui.theme.css',
            'css/chosen.css'
        ),
        'output_filename': 'css/master.r?.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'twenty': {
        'source_filenames': (
            'css/screen.css',
            'css/custom.css',
            'css/20m.css',
            'css/plugins/ui/jquery.ui.core.css',
            'css/plugins/ui/jquery.ui.datepicker.css',
            'css/plugins/ui/jquery.ui.tabs.css',
            'css/plugins/ui/jquery.ui.theme.css',
            'css/chosen.css'
        ),
        'output_filename': 'css/twenty.r?.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'mobile': {
        'source_filenames': (
            'css/mobile.css',
        ),
        'output_filename': 'css/mobile.r?.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'nc': {
        'source_filenames': (
            'css/screen.css',
            'css/custom.css',
            'css/nc.css',
            'css/plugins/ui/jquery.ui.core.css',
            'css/plugins/ui/jquery.ui.datepicker.css',
            'css/plugins/ui/jquery.ui.tabs.css',
            'css/plugins/ui/jquery.ui.theme.css',
            'css/chosen.css'
        ),
        'output_filename': 'css/nc.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    },
    'uk': {
        'source_filenames': (
            'css/screen.css',
            'css/custom.css',
            'css/uk.css',
            'css/plugins/ui/jquery.ui.core.css',
            'css/plugins/ui/jquery.ui.datepicker.css',
            'css/plugins/ui/jquery.ui.tabs.css',
            'css/plugins/ui/jquery.ui.theme.css',
            'css/chosen.css'
        ),
        'output_filename': 'css/uk.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    },
    'dcns': {
        'source_filenames': (
            'css/dcns/screen.css',
            'css/dcns/custom.css',
            'css/plugins/ui/jquery.ui.core.css',
            'css/plugins/ui/jquery.ui.datepicker.css',
            'css/plugins/ui/jquery.ui.tabs.css',
            'css/plugins/ui/jquery.ui.theme.css',
            'css/chosen.css'
        ),
        'output_filename': 'css/dcns.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    },
    'ie': {
        'source_filenames': (
            'css/ie/ie.css',
        ),
        'output_filename': 'css/ie.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    },
    'ie6': {
        'source_filenames': (
            'css/ie/ie6.css',
        ),
        'output_filename': 'css/ie6.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    },
    'ie7': {
        'source_filenames': (
            'css/ie/ie7.css',
        ),
        'output_filename': 'css/ie7.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    },
    'sep': {
        'source_filenames': (
            'css/sep/screen.css',
            'css/sep/custom.css'
        ),
        'output_filename': 'css/sep/master.r?.css',
        'extra_context': {
            'media': 'screen',
        }
    }
}

COMPRESS_JS = {
    'application': {
        'source_filenames': (
            'js/jquery.js',
            'js/ui/jquery.ui.core.js',
            'js/ui/jquery.ui.widget.js',
            'js/ui/jquery.ui.datepicker.js',
            'js/ui/jquery.ui.datepicker-fr.js',
            'js/ui/jquery.ui.tabs.js',
            'js/modernizr.js',
            'js/mustache.js',
            'js/jquery.cycle.all.latest.js',
            'js/jquery.autocomplete.js',
            'js/chosen.jquery.min.js',
            'js/application.js'),
        'output_filename': 'js/application.r?.js',
        'extra_context': {
            'defer': True,
        },
    },
    'sep': {
        'source_filenames': (
            'js/jquery.js',
            'js/sep/application.js'),
        'output_filename': 'js/sep/application.r?.js',
        'extra_context': {
            'defer': True,
        },
    }
}

# South configuration
SOUTH_TESTS_MIGRATE = getattr(local, 'SOUTH_TESTS_MIGRATE', True)

# Haystack configuration
HAYSTACK_SITECONF = 'eloue.sites'
HAYSTACK_SEARCH_ENGINE = getattr(local, 'HAYSTACK_SEARCH_ENGINE', 'solr')
HAYSTACK_SOLR_URL = getattr(local, 'HAYSTACK_SOLR_URL', 'http://localhost:8983/solr')
HAYSTACK_INCLUDE_SPELLING = True
HAYSTACK_ENABLE_REGISTRATIONS = True
SEARCH_QUEUE_LOG_LEVEL = logging.INFO

# Queue configuration
if DEBUG:
    QUEUE_BACKEND = 'dummy'
else:
    QUEUE_BACKEND = 'redisd'
QUEUE_REDIS_CONNECTION = getattr(local, 'QUEUE_REDIS_CONNECTION', 'localhost:6379')
QUEUE_REDIS_DB = getattr(local, 'QUEUE_REDIS_DB', 1)

# Email configuration
EMAIL_BACKEND = getattr(local, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

# Logging configuration
try:
    import logbook
    import logbook.compat
    logbook.compat.redirect_logging()
    null_handler = logbook.NullHandler()
    if DEBUG:
        log_handler = logbook.StderrHandler(level=logbook.WARNING)
    else:
        log_handler = logbook.SyslogHandler(level=logbook.WARNING)
    null_handler.push_application()
    log_handler.push_application()
except ImportError:
    pass

# Lean configuration
LEAN_ENGAGEMENT_CALCULATOR = 'eloue.lean.PatronEngagementScoreCalculator'

# Geocoding API
YAHOO_API_KEY = 'nnZZkyvV34Fkk9DOWOpYJL7C41.ispEvSVAXbA3Dhu894gljv877.G6KewexGZKhs7S6dSwxCvM-'

# SSL configuration
USE_HTTPS = getattr(local, 'USE_HTTPS', True)
SESSION_COOKIE_SECURE = getattr(local, 'SESSION_COOKIE_SECURE', True)

# Storage configuration
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
else:
    DEFAULT_FILE_STORAGE = 'storages.backends.overwrite.OverwriteStorage'

# S3 configuration
AWS_ACCESS_KEY_ID = getattr(local, 'AWS_ACCESS_KEY_ID', 'AKIAJ3PXVVKSTM3WSZSQ')
AWS_SECRET_ACCESS_KEY = getattr(local, 'AWS_SECRET_ACCESS_KEY', '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')
AWS_STORAGE_BUCKET_NAME = getattr(local, 'AWS_STORAGE_BUCKET_NAME', 'eloue')
AWS_S3_CUSTOM_DOMAIN = getattr(local, 'AWS_S3_CUSTOM_DOMAIN', 'eloue.s3.amazonaws.com')
AWS_DEFAULT_ACL = getattr(local, 'AWS_DEFAULT_ACL', 'public-read')
AWS_AUTO_CREATE_BUCKET = getattr(local, 'AWS_AUTO_CREATE_BUCKET', False)
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926,public',
}

# Paypal configuration
USE_PAYPAL_SANDBOX = getattr(local, 'USE_PAYPAL_SANDBOX', DEBUG)
VALIDATE_IPN = getattr(local, 'VALIDATE_IPN', True)
PAYPAL_MERCHANT_REFERRAL = "Z6GVNB75VNCTU"
if USE_PAYPAL_SANDBOX:
    PAYPAL_API_USERNAME = getattr(local, 'PAYPAL_SANDBOX_API_USERNAME', "benoit_1300354701_biz_api1.e-loue.com")
    PAYPAL_API_PASSWORD = getattr(local, 'PAYPAL_SANDBOX_API_PASSWORD', "1300354722")
    PAYPAL_API_SIGNATURE = getattr(local, 'PAYPAL_SANDBOX_API_SIGNATURE', "An5ns1Kso7MWUdW4ErQKJJJ4qi4-A0HCXVSBNN6Gj25nz33zT0f6ZfAK")
    PAYPAL_API_APPLICATION_ID = getattr(local, 'PAYPAL_SANDBOX_API_APPLICATION_ID', 'APP-80W284485P519543T')
    PAYPAL_API_EMAIL = getattr(local, 'PAYPAL_API_EMAIL', 'test_1301562706_biz@e-loue.com') #TODO, maybe this address, bug of sandbox? benoit.woj@e-loue.com
    PAYPAL_COMMAND = "https://www.sandbox.paypal.com/webscr?%s"
else:
    PAYPAL_API_USERNAME = getattr(local, 'PAYPAL_API_USERNAME', "benoit.woj_api1.e-loue.com")
    PAYPAL_API_PASSWORD = getattr(local, 'PAYPAL_API_PASSWORD', "34Z24TURKD2FJXDX")
    PAYPAL_API_SIGNATURE = getattr(local, 'PAYPAL_API_SIGNATURE', "ATyjR-cGlnW5vguT2T3LQhvPyZkLAuciTdL9GTRAigYudx6OGB385TPR")
    PAYPAL_API_APPLICATION_ID = getattr(local, 'PAYPAL_API_APPLICATION_ID', 'APP-2DL1603058460020J')
    PAYPAL_API_EMAIL = getattr(local, 'PAYPAL_API_EMAIL', "benoit.woj@e-loue.com")
    PAYPAL_COMMAND = "https://www.paypal.com/webscr?%s"

# Business configuration
BOOKING_DAYS = 85  # Max booking days
COMMISSION = 0.15  # Our commission percentage
POLICY_NUMBER = None  # Our insurance policy number
PARTNER_NUMBER = None  # Our insurance partner number
INSURANCE_FEE = 0.054  # Use to calculate transfer price
INSURANCE_TAXES = 0.09  # Use to calculate taxes on insurance
INSURANCE_FTP_HOST = None  # Our insurance ftp server host
INSURANCE_FTP_USER = None  # Our insurance ftp server username
INSURANCE_FTP_PASSWORD = None  # Our insurance ftp server password
INSURANCE_FTP_CWD = None  # Our insurance ftp server directory
INSURANCE_EMAIL = None  # Our insurance email

# Search configuration
DEFAULT_RADIUS = 215

# OAuth configuration
OAUTH_PROVIDER_KEY_SIZE = 32
OAUTH_AUTHORIZE_VIEW = "eloue.accounts.views.oauth_authorize"
OAUTH_CALLBACK_VIEW = "eloue.accounts.views.oauth_callback"

# Performance configuration
USE_ETAGS = False

# Affiliation configuraton
AFFILIATION_SOURCES = getattr(local, 'AFFILIATION_SOURCES', ['lv', 'skiplanet.equipment', 'jigsaw', 'kiloutou', 'loxam', 'chronobook'])
AFFILIATION_BATCHSIZE = 1000
LV_FTP = "ftp.bo.location-et-vacances.com"

# Camo configuration
CAMO_KEY = getattr(local, 'CAMO_KEY', 'OKNZYL69Ml3oISfEmJvtzFjhUeBbugxPDXanydwi4HGWrRTqcQ')

# Mobile configuration
MOBILE = getattr(local, 'MOBILE', False)
MOBILE_REDIRECT_BASE = getattr(local, 'MOBILE_REDIRECT_BASE', 'https://m.e-loue.com')

# Franc Pacifique
CONVERT_XPF = False
XPF_EXCHANGE_RATE = '0.00838'

# Message 
REPLACE_STRING = getattr(local, "REPLACE_STRING", "XXXXXX")


