# -*- coding: utf-8 -*-
import os
import logging
import decimal
import analytics
from getenv import env

from eloue.settings_utils import algolia_category_facets, \
    algolia_category_attributes_for_faceting, agolia_category_facet_name

local_path = lambda path: os.path.join(os.path.dirname(__file__), path)

DEBUG = env('DEBUG', True)
STAGING = env('STAGING', False)
CLIENT_EXCEPTION_LOGGING = env('CLIENT_EXCEPTION_LOGGING', False)
DEBUG_TOOLBAR = env('DEBUG_TOOLBAR', DEBUG)
TEMPLATE_DEBUG = DEBUG

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
#    'debug_toolbar.panels.redirects.RedirectsPanel',
] + env('DEBUG_TOOLBAR_PANELS', [])

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': set(),
}
DEBUG_TOOLBAR_CONFIG.update(env('DEBUG_TOOLBAR_CONFIG', {}))

ADMINS = (
    ('Operational Team', 'ops@e-loue.com'),
)

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

# Email configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
SERVER_EMAIL = 'contact@e-loue.com'
DEFAULT_FROM_EMAIL = 'contact@e-loue.com'
EMAIL_HOST = env('EMAIL_HOST', 'smtp.postmarkapp.com')
EMAIL_USE_TLS = env('EMAIL_USE_TLS', True)
EMAIL_PORT = env('EMAIL_PORT', 2525)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(),
}
DATABASES['default'].update({
    'OPTIONS': {'autocommit': env('DATABASE_OPTIONS_AUTOCOMMIT', True)},
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
})

POSTGIS_VERSION = (2, 1, 2)

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']


if env('REDISGREEN_URL', None):
    from urlparse import urlparse

    redisgreen = urlparse(env("REDISGREEN_URL"))

    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%i' % (redisgreen.hostname, redisgreen.port),
            'OPTIONS': {
                'DB': 1,
                'PASSWORD': redisgreen.password,
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': env('CACHE_BACKEND', 'django.core.cache.backends.dummy.DummyCache'),
            'LOCATION': env('CACHE_LOCATION', None),
        }
    }

# Cache configuration
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = env('CACHE_MIDDLEWARE_SECONDS', 60 * 15)
CACHE_MIDDLEWARE_KEY_PREFIX = env('CACHE_MIDDLEWARE_KEY_PREFIX', None)


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
LANGUAGE_CODE = env("LANGUAGE_CODE", 'fr-FR')

ugettext = lambda s: s
LANGUAGES = (
    ('fr', ugettext('Francais')),
    ('en', ugettext('English')),
    ('da', ugettext('Danish')),
    ('en-US', ugettext('English (United States)')),
    ('he', ugettext('Hebrews'))
)

LOCALE_PATHS = (local_path(os.path.join(os.path.pardir, 'locale/')), )


SITE_ID = 1
DEFAULT_SITES = env("DEFAULT_SITES", [1, 3, 4, 13, 14])

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
FORMAT_MODULE_PATH = 'eloue.formats'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = env('MEDIA_ROOT')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = env('MEDIA_URL')

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0j7jp$u!5n00s7=e@evlo0%ng&xm%zv^3-vn6gyy$&nbdd7p*('

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('eloue.compat.pyjade.loader.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        )
     ),
)
if not DEBUG:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'eloue.context_processors.site',
    'eloue.context_processors.debug',
    'eloue.context_processors.unread_message_count_context',
    'eloue.context_processors.facebook_context',
    'eloue.context_processors.analytics_context',
)


MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
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

if STAGING:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ("eloue.middleware.StagingRestrictionMiddleware",)

if CLIENT_EXCEPTION_LOGGING:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ("client_logging.middleware.ClientLoggingMiddleware",)


PASSWORD_HASHERS =(
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'accounts.auth.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher'
)

SSLIFY_DISABLE = env('SSLIFY_DISABLE', True)

if DEBUG_TOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# Urls configuration
ROOT_URLCONF = 'eloue.urls'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/dashboard/profil/'

TEMPLATE_DIRS = env('TEMPLATE_DIRS', ( local_path('templates/'), ))

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'modeltranslation',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sitemaps',
    'django.contrib.formtools',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'markup_deprecated', # 'django.contrib.markup',
    'django.contrib.gis',
    'mptt',
    'imagekit',
    'django_lean.experiments',
    'rollout',
    'pipeline',
    'announcements',
    'haystack',
    'queued_search',
    'django_messages',
    'oauth_provider',
    #'oauth2_provider', # django-oauth-toolkit
    'provider', 'provider.oauth2', # django-oauth2-provider
    'rest_framework',
    # 'faq',
    'accounts',
    'products',
    'rent',
    'shipping',
    'payments',
    'eloue.api',
    'south', # South must be the last in the list of applications that contains models
    'django_nose', # Make sure that django-nose comes after south in INSTALLED_APPS so that django_nose's test command is used.
    'core',
    'import_export',
    'djangular',
    #'django_faker',
)

if DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)

LOCAL_APPS = env('INSTALLED_APPS', None)
if LOCAL_APPS:
    INSTALLED_APPS += LOCAL_APPS


# Authentification configuration
AUTH_USER_MODEL = 'accounts.Patron'
ACCOUNT_ACTIVATION_DAYS = 7

# Tests configuration
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = env('NOSE_ARGS', ['--stop', '--with-doctest', '--cover-package=eloue', '--with-freshen', '--cover-branches'])
NOSE_PLUGINS = env('NOSE_PLUGINS', [])

# Message configuration
MESSAGE_STORAGE = env('MESSAGE_STORAGE', 'django.contrib.messages.storage.session.SessionStorage')

# Session configuration
SESSION_ENGINE = env('SESSION_ENGINE')
SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN')

# staticfiles configuration
STATIC_ROOT = 'staticfiles'
STATIC_URL = env('STATIC_URL', '/static/')
STATICFILES_DIRS = [local_path('static/'), ]
STATICFILES_STORAGE = env('STATICFILES_STORAGE', 'eloue.compat.pipeline.storage.PipelineCachedStorage')
STATICFILES_FINDERS = (
    #'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'eloue.compat.pipeline.finders.FixedPipelineFinder',
    'eloue.compat.pipeline.finders.FileSystemFinder',
    'eloue.compat.pipeline.finders.AppDirectoriesFinder',
    'eloue.compat.pipeline.finders.TemplatesFileSystemFinder',
)

#imagekit configuration
IMAGEKIT_SPEC_CACHEFILE_NAMER = 'imagekit.cachefiles.namers.source_name_dot_hash'
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = 'eloue.legacy.GenerateOptimistic' # 'imagekit.cachefiles.strategies.Optimistic'
IMAGEKIT_BATCH_GENERATION_CACHE_LIFETIME = env('IMAGEKIT_BATCH_GENERATION_CACHE_LIFETIME', 60 * 60 * 24 * 7)  # 7 days

#pipeline configuration
PIPELINE_ENABLED = env('PIPELINE', not DEBUG)
PIPELINE_DISABLE_WRAPPER = True # FIXME: fix collectstatic
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_COMPILERS = (
    #'pipeline.compilers.less.LessCompiler',
    'eloue.compat.pipeline.compilers.AutoprefixerSASSCompiler',
)
#PIPELINE_LESS_BINARY = env('PIPELINE_LESS_BINARY', '/home/benoitw/node_modules/less/bin/lessc')
PIPELINE_SASS_BINARY = env('PIPELINE_SASS_BINARY', '/usr/bin/sass')
PIPELINE_SASS_ARGUMENTS = '-q'
PIPELINE_YUGLIFY_BINARY = env('PIPELINE_YUGLIFY_BINARY', '/usr/bin/env yuglify')
PIPELINE_RJS_BINARY = env('PIPELINE_RJS_BINARY', '/app/node_modules/requirejs/bin/r.js')
PIPELINE_AUTOPREFIXER_BINARY = env('PIPELINE_AUTOPREFIXER_BINARY', '/app/node_modules/autoprefixer/autoprefixer')
PIPELINE_AUTOPREFIXER_ARGUMENTS = '-m --sources-content'
PIPELINE_CSS = {
    'extrastyles': {
        'source_filenames': (
            'fonts/flaticons_social/flaticons_social.css',
            'fonts/flaticons_solid/flaticons_solid.css',
            'fonts/flaticons_stoke/flaticons_stoke.css',
            'bower_components/chosen/chosen.min.css',
            'bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar.css',
            'bower_components/bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
            'bower_components/nprogress/nprogress.css',
            'bower_components/toastr/toastr.min.css',
        ),
        'output_filename': 'css/extra.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'bootstrap': {
        'source_filenames': (
            'sass/bootstrap.scss',
        ),
        'output_filename': 'css/bootstrap.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'homepage_styles': {
        'source_filenames': (
            'sass/homepage_styles.sass',
        ),
        'output_filename': 'css/homepage_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'product_list_styles': {
        'source_filenames': (
            'css/jslider.css', # temporary use our own hacked version of jQuery-UI styles to get green sliders
            'sass/product_list_styles.sass',
            #'bower_components/jqueryui/themes/smoothness/jquery-ui.min.css',
            'bower_components/bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
            'bower_components/angularjs-slider/dist/rzslider.css',
        ),
        'output_filename': 'css/product_list_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'product_detail_styles': {
        'source_filenames': (
            'sass/product_detail_styles.sass',
        ),
        'output_filename': 'css/product_detail_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'publish_item_styles': {
        'source_filenames': (
            'sass/publish_item_styles.sass',
        ),
        'output_filename': 'css/publish_item_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'how_it_works_styles': {
        'source_filenames': (
            'sass/how_it_works.sass',
        ),
        'output_filename': 'css/how_it_works_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'subscription_styles': {
        'source_filenames': (
            'sass/subscription_styles.sass',
        ),
        'output_filename': 'css/subscription_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'contact_us_styles': {
        'source_filenames': (
            'sass/contact_us_styles.sass',
        ),
        'output_filename': 'css/contact_us_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'security_styles': {
        'source_filenames': (
            'sass/security_styles.sass',
        ),
        'output_filename': 'css/security_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'press_styles': {
        'source_filenames': (
            'sass/press_styles.sass',
        ),
        'output_filename': 'css/press_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'profile_public_styles': {
        'source_filenames': (
            'sass/profile_public_styles.sass',
        ),
        'output_filename': 'css/profile_public_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'dashboard_styles': {
        'source_filenames': (
            'dashboard/sass/base.sass',
            'dashboard/sass/styles.sass',
        ),
        'output_filename': 'css/dashboard_styles.css',
        'extra_context': {
            'media': 'screen',
        },
    },
    'smartbanner_styles': {
        'source_filenames': (
            'css/jquery.smartbanner.css',
        ),
        'output_filename': 'css/jquery.smartbanner.css',
        'extra_context': {
            'media': 'screen',
        },
    },
}

PIPELINE_JS = {
    'require_js': {
        'source_filenames': (
            'bower_components/requirejs/require.js',
        ),
        'output_filename': 'js/require.js',
        'extra_context': {
            #'defer': False,
            #'async': False,
        },
    },
    'public_js': {
        'source_filenames': (
            'js/widgets/main.js',
        ),
        'output_filename': 'js/widgets.js',
        'template_name': 'pipeline/requirejs.html',
        'extra_context': {
            'build': 'js/widgets/build.js',
            'require_args': {'static-path': STATIC_URL},
            'requirejs': 'js/require.js' if PIPELINE_ENABLED else 'bower_components/requirejs/require.js',
            #'defer': False,
            #'async': False,
        },
    },
    'dashboard_js': {
        'source_filenames': (
            'js/dashboard/main.js',
        ),
        'output_filename': 'js/dashboard.js',
        'template_name': 'pipeline/requirejs.html',
        'extra_context': {
            'build': 'js/dashboard/build.js',
            'require_args': {'static-path': STATIC_URL},
            'requirejs': 'js/require.js' if PIPELINE_ENABLED else 'bower_components/requirejs/require.js',
            #'defer': False,
            #'async': False,
        },
    },
    # Scripts to be loaded before everything else
    # (e.g. progress bar or loading screen js)
    'priority_js': {
        'source_filenames': (
            'bower_components/nprogress/nprogress.js',
            'js/priority/*.js',
        ),
        'output_filename': 'js/priority.js',
    },
}

# South configuration
SOUTH_TESTS_MIGRATE = env('SOUTH_TESTS_MIGRATE', False)
SOUTH_MIGRATION_MODULES = {
    'announcements': 'eloue.migrations.announcements',
    'django_messages': 'eloue.migrations.django_messages',
    'auth': 'eloue.migrations.auth', # here we have Django 1.5+ new auth migration
}


# Haystack configuration

SEARCH_ENGINE = env('SEARCH_ENGINE', 'algolia')

ALGOLIA_CREDENTIALS = {
    'APP_ID': env('ALGOLIA_APP_ID', None),
    'API_KEY_SEARCH': env('ALGOLIA_API_KEY_SEARCH', None),
    'API_KEY_WRITE': env('ALGOLIA_API_KEY', None),
    'PREFIX': env('ALGOLIA_INDEX_PREFIX', 'e-loue_')
}

HAYSTACK_CONNECTIONS = {                
#    'elasticsearch': {
#         'ENGINE': 'eloue.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': env('ELASTICSEARCH_URL', '127.0.0.1:9200'),
#         'INDEX_NAME': env('ELASTICSEARCH_INDEX_NAME', 'eloue'),
#         'KWARGS': {
#             'use_ssl': env('ELASTICSEARCH_USE_SSL', False),
#             'http_auth': env('ELASTICSEARCH_HTTP_AUTH', None)
#         }
#     },              
    'algolia': {
        'ENGINE': 'eloue.search_backends.EloueAlgoliaEngine',
        'APP_ID': ALGOLIA_CREDENTIALS['APP_ID'],
        'API_KEY': ALGOLIA_CREDENTIALS['API_KEY_WRITE'],
        'INDEX_NAME_PREFIX': ALGOLIA_CREDENTIALS['PREFIX'],
        'TIMEOUT': 60 * 5
    },
}

HAYSTACK_CONNECTIONS['default'] = HAYSTACK_CONNECTIONS[SEARCH_ENGINE]


# Algolia configuration
ALGOLIA_INDICES = {
    "accounts.patron":{
        'attributesForFaceting': ['django_ct', 
                              'django_id',
                              'sites',
                              'sites_exact',
                              'username',
                              'date_joined_date',],
    },
    "products.product":{
        'customRanking': ['desc(featured)',
                          'desc(average_rate)', 
                          'desc(comment_count)'],
        'attributesToIndex': ['categories', 
                              'summary',
                              'description',],
        'attributesForFaceting': [
            u'algolia_categories.lvl0',
            u'algolia_categories.lvl1',
            u'algolia_categories.lvl2',
            u'categories',
            u'categories_exact',
            u'django_id_int',
            u'is_archived',
            u'is_good',
            u'pro_owner',
            u'sites',
            u'sites_exact',
            u'price',
            u'price_exact',
            u'owner',
            u'owner_exact',
            u'created_at_timestamp',
            u'is_allowed'] + algolia_category_attributes_for_faceting(LANGUAGES),
        'attributesToHighlight': ['summary'],
        'attributesToSnippet': ['description:50',],
        'highlightPreTag': '<em>',
        'highlightPostTag': '</em>',
        'removeStopWords':True,
        'hitsPerPage': 12,
        'ranking': [
            'typo',
#             'geo',
            'words',
            'filters',
            'proximity',
            'attribute',
            'exact',
            'custom'],
        "slaves":{
            "price":{
                'ranking': [
                    'typo',
                    'asc(price)',
#                     'geo',
                    'words',
                    'filters',
                    'proximity',
                    'attribute',
                    'exact',
                    'custom'],
            },
            "-price":{
                'ranking': [
                    'typo',
                    'desc(price)',
#                     'geo',
                    'words',
                    'filters',
                    'proximity',
                    'attribute',
                    'exact',
                    'custom'],
            },
            "-created_at":{
                'ranking': [
                    'typo',
                    'desc(created_at_timestamp)',
#                     'geo',
                    'words',
                    'filters',
                    'proximity',
                    'attribute',
                    'exact',
                    'custom'],
            },
            "distance":{
                'ranking': [
                    'typo',
                    'geo',
                    'words',
                    'filters',
                    'proximity',
                    'attribute',
                    'exact',
                    'custom'],
            },
        },
    },            
}


ALGOLIA_CLIENT_CONFIG = {
    'MASTER_INDEX': ALGOLIA_CREDENTIALS['PREFIX'] + 'products.product',
    'PARAMETERS': {
        'attributesToRetrieve':["summary", "django_id", "username", "description"
                "location", "locations", "city", "zipcode", "owner_url", 
                "owner_avatar", "url", "price", "profile", "vertical_profile",
                "thumbnail", "comment_count", "average_rate", "pro_owner"],
        'hierarchicalFacets': algolia_category_facets(LANGUAGES),
        'disjunctiveFacets': ["pro_owner",
                            "price",
                            "sites"],
        'facets': ["is_archived", 
                 'is_good',
                 'is_allowed'],
        'hitsPerPage': 12,
        'query':"",
        'snippetEllipsisText': "&hellip;",
    },
    'ALGOLIA_PREFIX': "sp_",
    'ALGOLIA_APP_ID': ALGOLIA_CREDENTIALS['APP_ID'],
    'ALGOLIA_KEY': ALGOLIA_CREDENTIALS['API_KEY_SEARCH'],
    'URL_PARAMETERS': ['query', 'page', 'aroundRadius', 
                       'attribute:pro_owner', 'attribute:price',
                       'attribute:'+agolia_category_facet_name(LANGUAGE_CODE)],
    'URL_PARAMETERS_EXCLUDE': ['is_archved', 
                             'is_good', 
                             'sites',
                             'is_allowed'],
    'PAGINATION_WINDOW_SIZE': 10
}


#HAYSTACK_SIGNAL_PROCESSOR = 'queued_search.signals.QueuedSignalProcessor'
HAYSTACK_SIGNAL_PROCESSOR = 'eloue.search.HaystackSignalProcessor'
SEARCH_QUEUE_LOG_LEVEL = logging.INFO

# Queue configuration
QUEUE_BACKEND = env('QUEUE_BACKEND', 'dummy')
QUEUE_REDIS_CONNECTION = env('QUEUE_REDIS_CONNECTION', 'localhost:6379')
QUEUE_REDIS_DB = env('QUEUE_REDIS_DB', 1)

REST_FRAMEWORK = {
#     'DEFAULT_RENDERER_CLASSES': (
#         'rest_framework.renderers.JSONRenderer',
#         'rest_framework.renderers.BrowsableAPIRenderer',
#         'rest_framework_plist.renderers.PlistRenderer',
#     ),
#     'DEFAULT_PARSER_CLASSES': (
#         'rest_framework.parsers.JSONParser',
#         'rest_framework.parsers.FormParser',
#         'rest_framework.parsers.MultiPartParser',
#         'rest_framework_plist.parsers.PlistParser',
#     ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'eloue.backends.EloueRestAuthBackend',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'eloue.api.permissions.DefaultPermissions',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': 'eloue.api.exceptions.api_exception_handler',
    'SEARCH_PARAM': 'q',
    'ORDERING_PARAM': 'ordering',
    'PAGINATE_BY': env('REST_FRAMEWORK_PAGINATE_BY', 10),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

OAUTH2_PROVIDER = {
    # this is the list of available scopes
    'SCOPES': {
        'end-user': 'End-users are borrower or/and owner, and have acces to e-loue where they can seach, publish ads, send messages to another end-user, call to an owner, book a product, comment a booking and manage all their actions in a dashboard.',
        'teamstaff': 'Team staff access to the administration interface to manage end-users, bookings and products. The access of data is restrected with permissions.',
        'superuser': 'Super user access to the administration interface to manage end-users, team staff, bookings, products, etc. He has all the permissions.',
    }
}

# Logging configuration

try:
    import logbook
    import logbook.compat
    from client_logging import util as cl_util 
    logbook.compat.redirect_logging()
    null_handler = logbook.NullHandler()
    if DEBUG:
        log_handler = logbook.StderrHandler(level=logbook.WARNING)
        if CLIENT_EXCEPTION_LOGGING:
            js_log_handler = logbook.StderrHandler(filter=cl_util.js_error_log_filter, level=logbook.INFO)
            js_log_handler.formatter = cl_util.js_error_formatter_stderr
    else:
        log_handler = logbook.SyslogHandler(level=logbook.WARNING)
        if CLIENT_EXCEPTION_LOGGING:
            js_log_handler = logbook.SyslogHandler(filter=cl_util.js_error_log_filter, level=logbook.INFO)
            js_log_handler.formatter = cl_util.js_error_formatter_syslog
    null_handler.push_application()
    log_handler.push_application()
    if CLIENT_EXCEPTION_LOGGING:
        js_log_handler.push_application()
except ImportError:
    pass


CLIENT_EXCEPTION_RATE = env('CLIENT_EXCEPTION_RATE', "20/hour")


logging.getLogger('suds.client').setLevel(logging.ERROR)
logging.getLogger('suds.transport').setLevel(logging.ERROR)
logging.getLogger('suds.xsd.schema').setLevel(logging.ERROR)
logging.getLogger('suds.wsdl').setLevel(logging.ERROR)

# Lean configuration
LEAN_ENGAGEMENT_CALCULATOR = 'eloue.lean.PatronEngagementScoreCalculator'

# Geocoding API
YAHOO_API_KEY = 'nnZZkyvV34Fkk9DOWOpYJL7C41.ispEvSVAXbA3Dhu894gljv877.G6KewexGZKhs7S6dSwxCvM-'

# SSL configuration
USE_HTTPS = env('USE_HTTPS', True)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', True)

# Storage configuration
DEFAULT_FILE_STORAGE = env('DEFAULT_FILE_STORAGE', 'storages.backends.overwrite.OverwriteStorage')

# S3 configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', '')
AWS_S3_SECURE_URLS = env('AWS_S3_SECURE_URLS', True)
AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL', 'public-read')
AWS_AUTO_CREATE_BUCKET = env('AWS_AUTO_CREATE_BUCKET', False)
AWS_HEADERS = {
    'Cache-Control': 'max-age=31556926,public',
}


#API KEYS
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', '218840159400.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET', 'BXFNFpDb6MN0ocLoPunjkzvZ')

FACEBOOK_APP_ID = env('FACEBOOK_APP_ID', '197983240245844')

IDN_CONSUMER_KEY = env('IDN_CONSUMER_KEY', '_ce85bad96eed75f0f7faa8f04a48feedd56b4dcb')
IDN_CONSUMER_SECRET = env('IDN_CONSUMER_SECRET', '_80b312627bf936e6f20510232cf946fff885d1f7')
IDN_BASE_URL = env('IDN_BASE_URL', 'http://idn.recette.laposte.france-sso.fr/')
IDN_RETURN_URL = env('IDN_RETURN_URL', 'http://localhost:8000/login/')

# Paypal configuration
USE_PAYPAL_SANDBOX = env('USE_PAYPAL_SANDBOX', DEBUG)
VALIDATE_IPN = env('VALIDATE_IPN', True)
PAYPAL_MERCHANT_REFERRAL = "Z6GVNB75VNCTU"
if USE_PAYPAL_SANDBOX:
    PAYPAL_API_USERNAME = env('PAYPAL_SANDBOX_API_USERNAME', "benoit_1300354701_biz_api1.e-loue.com")
    PAYPAL_API_PASSWORD = env('PAYPAL_SANDBOX_API_PASSWORD', "1300354722")
    PAYPAL_API_SIGNATURE = env('PAYPAL_SANDBOX_API_SIGNATURE', "An5ns1Kso7MWUdW4ErQKJJJ4qi4-A0HCXVSBNN6Gj25nz33zT0f6ZfAK")
    PAYPAL_API_APPLICATION_ID = env('PAYPAL_SANDBOX_API_APPLICATION_ID', 'APP-80W284485P519543T')
    PAYPAL_API_EMAIL = env('PAYPAL_API_EMAIL', 'test_1301562706_biz@e-loue.com') #TODO, maybe this address, bug of sandbox? benoit.woj@e-loue.com
    PAYPAL_COMMAND = "https://www.sandbox.paypal.com/webscr?%s"
else:
    PAYPAL_API_USERNAME = env('PAYPAL_API_USERNAME', "benoit.woj_api1.e-loue.com")
    PAYPAL_API_PASSWORD = env('PAYPAL_API_PASSWORD', "34Z24TURKD2FJXDX")
    PAYPAL_API_SIGNATURE = env('PAYPAL_API_SIGNATURE', "ATyjR-cGlnW5vguT2T3LQhvPyZkLAuciTdL9GTRAigYudx6OGB385TPR")
    PAYPAL_API_APPLICATION_ID = env('PAYPAL_API_APPLICATION_ID', 'APP-2DL1603058460020J')
    PAYPAL_API_EMAIL = env('PAYPAL_API_EMAIL', "benoit.woj@e-loue.com")
    PAYPAL_COMMAND = "https://www.paypal.com/webscr?%s"

# Business configuration
BOOKING_DAYS = 85  # Max booking days
COMMISSION = decimal.Decimal('0.2')  # Our commission percentage

POLICY_NUMBER = "AC477704"  # Our insurance policy number
PARTNER_NUMBER = "GRDT020"  # Our insurance partner number
INSURANCE_FTP_HOST = 'ftppartenaire.assurone.com'  # Our insurance ftp server host
INSURANCE_FTP_USER = 'eloue'  # Our insurance ftp server username
INSURANCE_FTP_PASSWORD = '0QsnTY5b'  # Our insurance ftp server password
INSURANCE_FTP_CWD = '/'  # Our insurance ftp server directory
INSURANCE_EMAIL = 'benoit.woj@e-loue.com'  # Our insurance email

INSURANCE_FEE_NORMAL = decimal.Decimal('0.0459')

INSURANCE_FEE_CAR = decimal.Decimal('0.1')
INSURANCE_FEE_REALESTATE = decimal.Decimal('0.035')

INSURANCE_TAXES_NORMAL = decimal.Decimal('0.09')
INSURANCE_TAXES_CAR = decimal.Decimal('0')
INSURANCE_TAXES_REALESTATE = decimal.Decimal('0')

INSURANCE_COMMISSION_REALESTATE = INSURANCE_COMMISSION_CAR = INSURANCE_COMMISSION_NORMAL = decimal.Decimal('0')

INSURANCE_AVAILABLE = True

# Search configuration
DEFAULT_RADIUS = 215

# OAuth configuration
OAUTH_PROVIDER_KEY_SIZE = 32
OAUTH_AUTHORIZE_VIEW = 'accounts.views.oauth_authorize'
OAUTH_CALLBACK_VIEW = 'accounts.views.oauth_callback'

# Performance configuration
USE_ETAGS = False

# Affiliation configuraton
AFFILIATION_SOURCES = env('AFFILIATION_SOURCES', ['lv', 'skiplanet.equipment', 'jigsaw', 'loxam', 'chronobook', 'monjoujou'])
AFFILIATION_BATCHSIZE = 1000
LV_FTP = "ftp.bo.location-et-vacances.com"

# Camo configuration
CAMO_KEY = env('CAMO_KEY', 'OKNZYL69Ml3oISfEmJvtzFjhUeBbugxPDXanydwi4HGWrRTqcQ')

# Mobile configuration
MOBILE = env('MOBILE', True)
MOBILE_REDIRECT_BASE = env('MOBILE_REDIRECT_BASE', 'https://m.e-loue.com')

# Franc Pacifique
CONVERT_XPF = False
XPF_EXCHANGE_RATE = '0.00838'

# Message 
REPLACE_STRING = env("REPLACE_STRING", "XXXXXX")

DEFAULT_LOCATION = env("DEFAULT_LOCATION", {
    'city': u'Paris',
    'coordinates': (48.856614, 2.3522219),
    'country': u'France',
    'country_coordinates': (46.2, 2.2),
    'country_radius': 800,
    'fallback': None,
    'radius': 11,
    'formatted_address': u'Paris, France',
    'region': u'Île-de-France',
    'region_coords': (48.8499198, 2.6370411),
    'region_radius': 100,
    'source': 4
})

DEFAULT_LOCATION_CITY = None

USE_PAYBOX_SANDBOX = env('USE_PAYBOX_SANDBOX', DEBUG)
if USE_PAYBOX_SANDBOX:
    PAYBOX_VERSION = env('PAYBOX_VERSION', '00104')
    PAYBOX_SITE = env('PAYBOX_SITE', 1999888)
    PAYBOX_RANG = env('PAYBOX_RANG', 99)
    PAYBOX_CLE = env('PAYBOX_CLE', '1999888I')
    PAYBOX_DEVISE = env('PAYBOX_DEVISE', 978)
    PAYBOX_ACTIVITE = env('PAYBOX_ACTIVITE', '027')
    PAYBOX_ENDPOINT = env('PAYBOX_ENDPOINT', "https://preprod-ppps.paybox.com/PPPS.php")
else:
    PAYBOX_SITE = env('PAYBOX_SITE', '3818292')
    PAYBOX_RANG = env('PAYBOX_RANG', '01')
    PAYBOX_DEVISE = env('PAYBOX_DEVISE', 978)
    PAYBOX_ACTIVITE = env('PAYBOX_ACTIVITE', '027')
    PAYBOX_ENDPOINT = env('PAYBOX_ENDPOINT', "https://ppps.paybox.com/PPPS.php")
    PAYBOX_VERSION = env('PAYBOX_VERSION', '00104')
    PAYBOX_CLE = env('PAYBOX_CLE', 'IJEDEDBC')


## NAVETTE PICKCUP CONFIGURATION
NAVETTE_ENDPOINT = env('NAVETTE_ENDPOINT', 'http://test-web-navette.pickup.fr/v1/Navette.svc?wsdl')
NAVETTE_FILE_TRANSFER_ENDPOINT = env('NAVETTE_FILE_TRANSFER_ENDPOINT', 'http://test-web-navette.pickup.fr/v1/FileTransfer.svc?wsdl')
WSDL_PROXY = env('WSDL_PROXY',
        {'http': 'http://proxy:aa2d0de6b805-416d-91b9-3e586917597c@proxy-54-75-227-164.proximo.io',})


PRODUCTHIGHLIGHT_PRICE = decimal.Decimal('7.5')
PRODUCTTOPPOSITION_PRICE = decimal.Decimal('5.5')
EMAILNOTIFICATION_PRICE = decimal.Decimal('0.01')
SMSNOTIFICATION_PRICE = decimal.Decimal('0.08')

TVA = decimal.Decimal('0.196')

GA_PING_QUEUE_CONNECTION = ('localhost', 6379, 1)
GA_PING_QUEUE_NAME = 'ga_queue'


GOOGLE_CLIENT_SECRETS = env('GOOGLE_CLIENT_SECRETS', '')
GOOGLE_TOKEN_FILE_NAME = env('GOOGLE_TOKEN_FILE_NAME', '')

SLIMPAY_SCIM_HOME = env('SLIMPAY_SCIM_HOME', '')
SLIMPAY_LOGGER_CONFIG = env('SLIMPAY_LOGGER_CONFIG', '')
SLIMPAY_SCIM_JAR_FILE = env('SLIMPAY_SCIM_JAR_FILE', '')
SLIMPAY_SITE_ID = env('SLIMPAY_SITE_ID', '')

VIVA_SITE_ID = env('VIVA_SITE_ID', '45364001')


NON_ACTIVE_LOGIN_COUNT = 1

AUTHENTICATION_BACKENDS = (
    'eloue.backends.EloueAuthBackend',
)

NAVBAR_CATEGORIES = env('NAVBAR_CATEGORIES', [
    35, 390, 253, 418, 3, 379, 126, 172,  # first line / nav bar
    432, 323, 297, 512, 2700, 335, 495, 2713  # others / dropdown selection
])

FILTER_CATEGORIES = env('FILTER_CATEGORIES', tuple())

PUBLISH_CATEGORIES = env('PUBLISH_CATEGORIES', tuple())

TEST_MODE = False

# Analytics services IDs. Replace these for each site
ANALYTICS = {
             'FACEBOOK_ID': '631094037033631',
             'GOOGLE_ID': 'UA-8258979-1',
             'SEGMENT_ID': 'CK4wf1QXZEjeqFRo75zZQ7DfZWzYJwHC',
             }

if not DEBUG:
    IMPORT_EXPORT_TMP_STORAGE_CLASS = "import_export.tmp_storages.MediaStorage"


#Parse credential
PARSE_APPLICATION_ID = env('PARSE_APPLICATION_ID', '1WuJlTny9WGUINnphSb8kPbCOUUgymck6n8PwmYE')
PARSE_REST_API_KEY = env('PARSE_REST_API_KEY', 'VQdNVFgacql3M7T1uTnk8jO7mjqM3Q5yCiaqyXyv')

ANALYTICS_WRITE_KEY = env('ANALYTICS_WRITE_KEY', 'CK4wf1QXZEjeqFRo75zZQ7DfZWzYJwHC')
