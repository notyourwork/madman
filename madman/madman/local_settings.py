LOCAL_SETTINGS = True 

from madman import media_processor 
from settings import * 

DEBUG = True

TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'madmanDjango',                      
        'USER': 'root',         
        'PASSWORD': 'ttoorr',           
        'HOST': '', 
        'PORT': '',             
    }
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'madman.db',                      
        'USER': '',         
        'PASSWORD': '',           
        'HOST': '', 
        'PORT': '',             
    }
}

SECRET_KEY = 'gxhr1css-@8&^x-&16trb09rprbsh#su__*@^#b1f@k-=1*o1='

TIME_ZONE = 'America/New_York'

MEDIA_ROOT = os.path.join(PUBLIC_DIR, 'media') 
MEDIA_ROOT = '/var/www/sitemedia/django/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://sitemedia.notyourwork.com/woark/media/'
MEDIA_URL = 'http://sitemedia.notyourwork.com/madman/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PUBLIC_DIR, 'static')
STATIC_ROOT = '/var/git/mad-man/mysite/static/' 

# URL prefix for static files.
STATIC_URL = 'http://sitemedia.notyourwork.com/madman/'

#email settings 
EMAIL_HOST = "localhost"
DEFAULT_FROM_EMAIL = "noreply@notyourwork.com"
EMAIL_PORT = 25
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Cache backend - use dummy cache for dev  
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
	        'filename' : os.path.join(PROJECT_DIR, 'logs/mylog.log'), 
            'maxBytes': 1024*1024*2, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },  
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename' : os.path.join(PROJECT_DIR, 'logs/django_request.log'), 
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

if DEBUG:

    # Add in django debug toolbar 
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INTERNAL_IPS = ('127.0.0.1', '76.181.251.8', )
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
        'debug_toolbar.panels.version.VersionDebugPanel',
    )
    INSTALLED_APPS += (
        'debug_toolbar', 
    )
    def custom_show_toolbar(request):
        return True  

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
        'HIDE_DJANGO_SQL': False,
        'SHOW_TEMPLATE_CONTEXT': True, 
        'TAG': 'div',
        'ENABLE_STACKTRACES' : True,
    }
MADMAN_DOWNLOAD_PLACES = [
    #'/media/downloads/ircdownloads/complete/',
    '/media/downloads/seeding/',
]

MADMAN_SEEDING_PLACES = [    
    '/media/downloads/seeding', 
]

MADMAN_MEDIA_CONFIG  = {
    'hd movies' : (
        media_processor.movie_processor,
        ('/media/hdmovies1', "[0-9A-E]"), 
        ('/media/hdmovies2', '[F-L]'), 
        ('/media/hdmovies3', '[M-R]'), 
        ('/media/hdmovies4', '[S-Z]'), 
    ),
    'movies' : (
        media_processor.movie_processor, 
        ('/media/movies1', '[(0-9A-Z]'), 
    ), 
    'tv' : (
        media_processor.tv_processor, 
        ('/media/tv1/', '[0-9A-J]' ), 
        ('/media/tv2', '[K-Z]' ),  
    ),
    'hd tv' : (
        media_processor.tv_processor, 
        ('/media/hdtv1','[0-9A-H]' ),
        ('/media/hdtv2','[I-Q]' ),
        ('/media/hdtv3', '[R-S]' ),
    ),
    'music' : (
        ('/media/music1/', '[0-9A-G]' ),
    )
}

#ordered by preference
MADMAN_MEDIA_CONFIG_2  = {
    'video' : {
        'hd movies' : {
            'fn' : 'movie_processor',
            'dirs' :[
                ('/media/hdmovies1', "[0-9A-E]"), 
                ('/media/hdmovies2', '[F-L]'), 
                ('/media/hdmovies3', '[M-R]'), 
                ('/media/hdmovies4', '[S-Z]'),
            ],
            'defn' : "([^\\/]*)(\d{4})([^\\/]*)",
            'min_size' : 1024*1024*1024*1024*2
        },
        'hd tv' : {
            'fn' : 'hd_tv_processor', 
            'dirs' : [
                ('/media/hdtv1','[0-9A-H]' ),
                ('/media/hdtv2','[I-Q]' ),
                ('/media/hdtv3', '[R-S]' ),
                ('min_size' , 1024*1024*1024*1024*2 ),
            ],
        },
        'movies' : {
            'fn' : 'movie_processor', 
            'dirs' : [
                ('/media/movies1', '[(0-9A-Z]'), 
            ],
            'defn' : "([^\\/]*)(\d{4})([^\\/]*)",
        },
        'tv' : {
            'fn' : 'tv_processor', 
            'dirs' : [
                ('/media/tv1/', '[0-9A-J]' ), 
                ('/media/tv2', '[K-Z]' ),  
            ],
            'defn' : '',
        },
    },
    'audio' : {
        'music' : {
            'fn' : 'music_processor',
            'dirs' : [
                ('/media/music1/', '[0-9A-G]' ),
            ],
            'defn':'',
        },
    },
}



