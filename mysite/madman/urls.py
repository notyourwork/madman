from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('madman.views',
    (r'^$', 'index'),
    url(r'^location/$', 'medialocation', name='medialocation_list'),    
    url(r'^type/(?P<id>\d+)/$', 'mediatype', name='mediatype'),    
    url(r'^location/(?P<id>\d+)/$', 'medialocation', name='medialocation'),    
    url(r'^file/(?P<id>\d+)/$', 'mediafile', name='mediafile'),
    url(r'^type/(?P<id>\d+)/$', 'mediatype', name='mediatype'),
    url(r'^rules/$', 'template',{'type': 'rules'}),
    url(r'^report/$', 'report', name='report'),

)

