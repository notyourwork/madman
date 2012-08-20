import os, logging, socket, django, imp 

# Django settings for mysite project.
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS


# calculated paths for django and the site
# used as starting points for various other paths
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

#configure logging and format 
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
FORMAT='%(asctime)s - %(levelname)s\n%(message)s\n--------------------------------'

logging.basicConfig( level=logging.ERROR, format=FORMAT, )

# https://docs.djangoproject.com/en/dev/ref/settings/#time-zone 
TIME_ZONE = 'America/New_York'
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True 
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = ''
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = ''
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = ''
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = ''


STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages"
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)


if DEBUG:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)
if USE_I18N:
    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.i18n',)
if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

ROOT_URLCONF = 'mysite.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    #added 
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize', 
    'django.contrib.comments',      #django commenting  
    'registration', 
    'profiles', 
    'taggit',                   #for tagging jobs, bids, pitches and such 
    'madman', 
    'django_extensions', 
    'mptt',
    'compressor',  
    'mailer', 
    'contact_form',             #django contact-form app 
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}
AUTH_PROFILE_MODULE = 'madman.UserProfile'

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window

#Add in any "templates" directories inside SITE_ROOT 
TEMPLATE_DIRS = ()
for root, dirs, files in os.walk(SITE_ROOT):
    if 'templates' in dirs: TEMPLATE_DIRS += (os.path.join(root, 'templates'),)

#import madman settings 
try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import * 
    except ImportError:
        print "Error importing local madman settings, please copy local_settings_dist.py to local_settings.py."

