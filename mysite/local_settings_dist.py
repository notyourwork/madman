LOCAL_SETTINGS = True
import settings 
import socket 
from madman import media_processor 

DEBUG = True
# Set DEBUG = True if on the production server
if socket.gethostname() == 'media.notyourwork.com':
    DEBUG = False
else:
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

SECRET_KEY = 'gxhr1css-@8&^x-&16trb09rprbsh#su__*@^#b1f@k-=1*o1='

TIME_ZONE = 'America/New_York'

MEDIA_ROOT = '/var/www/sitemedia/django/'

MEDIA_URL = 'http://sitemedia.notyourwork.com/madman/media/'

#STATIC_ROOT = '/var/www/sitemedia/django/static/'
STATIC_ROOT = '/var/git/mad-man/mysite/static/' 

STATIC_URL = 'http://sitemedia.notyourwork.com/madman/'

ADMIN_MEDIA_PREFIX = 'http://sitemedia.notyourwork.com/django/'

STATICFILES_DIRS = (
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

MADMAN_DOWNLOAD_PLACES = [
    #'/media/downloads/ircdownloads/complete/',
    '/media/downloads/seeding/',
]

MADMAN_SEEDING_PLACES = [    
    '/media/downloads/seeding', 
]

MADMAN_MEDIA_PLACES = [
    '/media/hdmovies1',
    '/media/hdmovies2',
    '/media/hdmovies3',
    '/media/hdmoves4',
    '/media/movies1',
    '/media/hdtv1',
    '/media/hdtv2',
    '/media/tv1',
    '/media/tv2',
]

MADMAN_MEDIA_CONFIG  = {
    'hdmovies' : (
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
    'hdtv' : (
        media_processor.tv_processor, 
        ('/media/hdtv1','[0-9A-H]' ),
        ('/media/hdtv2','[I-Q]' ),
        ('/media/hdtv3', '[R-S]' ),
    ),
    'music' : (
        ('/media/music1/', '[0-9A-G]' ),
    )
}
