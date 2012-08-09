from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'madman.views.index', name="home"),    
    url(r'^accounts/', include('registration.urls')),
    #use to override django view for login 
    #(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'myapp/login.html'}),
    (r'^madman/', include('madman.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),    
    (r'^admin/', include(admin.site.urls)),

)

