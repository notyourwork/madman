from django.conf.urls import patterns, include, url
from django.contrib import admin
from madman.forms import UserProfileForm

admin.autodiscover()

urlpatterns = patterns('',
    #django home page 
    url(r'^$', 'madman.views.index', name="home"),    

    #django accounts 
    url(r'^accounts/', include('registration.urls')),

    #commenting framework 
    (r'^comments/', include('django.contrib.comments.urls')),    

    #django admin section 
    url(r'^admin/', include(admin.site.urls)),
    
    #django profiles 
    url(
        r'^profiles/edit/', 
        'profiles.views.edit_profile', 
        {'form_class':UserProfileForm,},
        name='edit_profile'
    ),
    #default rest of the profile section
    url(r'^profiles/', include('profiles.urls')),
)

urlpatterns += patterns('madman.views',
    url(r'^location/$', 'medialocation', name='medialocation_list'),    
    url(r'^type/(?P<id>\d+)/$', 'mediatype', name='mediatype'),    
    url(r'^location/(?P<id>\d+)/$', 'medialocation', name='medialocation'), 
    url(r'^file/(?P<id>\d+)/$', 'mediafile', name='mediafile'),
    url(r'^type/(?P<id>\d+)/$', 'mediatype', name='mediatype'),
    url(r'^rules/$', 'template',{'type': 'rules'}),
    url(r'^report/$', 'report', name='report'),
)

