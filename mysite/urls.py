from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from madman.forms import UserProfileForm
urlpatterns = patterns('',
    url(r'^$', 'madman.views.index', name="home"),    
    url(r'^accounts/', include('registration.urls')),
    #use to override django view for login 
    #(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'myapp/login.html'}),
    (r'^madman/', include('madman.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),    
    (r'^admin/', include(admin.site.urls)),
    url(
        r'^profiles/edit/', 
        'profiles.views.edit_profile', 
        {'form_class':UserProfileForm,},
        name='edit_profile'
    ),
    (r'^profiles/', include('profiles.urls')), 
)

