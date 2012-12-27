from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from madman.forms import UserProfileForm
urlpatterns = patterns('',
    url(r'^$', 'madman.views.index', name="home"),    
    (r'^madman/', include('madman.urls')),
    
    url(r'^accounts/', include('registration.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),    
    (r'^admin/', include(admin.site.urls)),
    url(
        r'^profiles/edit/', 
        'profiles.views.edit_profile', 
        {'form_class':UserProfileForm,},
        name='edit_profile'
    ),
        #default rest of the profile section
    url(r'^profiles/', include('profiles.urls')),
)

