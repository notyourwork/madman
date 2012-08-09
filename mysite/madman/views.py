from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Context, loader
from madman.models import * 
from django.db.models import Avg, Max, Min, Count

from django.core.mail import send_mail
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_protect, requires_csrf_token
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.cache import cache_page

import datetime, random, sha

#madman home page 
#displays current locations and recent file additions 


#set django custom 404 handler 
handler404 = 'madman.error_views.custom_404'
handler500 = 'madman.error_views.custom_500'
handler403 = 'madman.error_views.custom_403'

@login_required
def index( request ):
    media_types = MediaType.objects.all() 
    current_locations = MediaLocation.objects.filter( parent=None ).order_by( 'name')
    newest_locations = MediaLocation.objects.all( ).order_by( 'created_time' )[ :5 ]
    latest_file_list = MediaFile.objects.all().order_by('created_time')[:5]
    return render(request, 'madman/main.html', locals() )

@login_required
def mediafilenewest( request ):
    latest_list = MediaFile.objects.all().order_by( '-created' )[ :5 ]
    output = ', '.join( [ f.name for f in latest_list ] )
    return HttpResponse( output )

@login_required 
def mediatype(request, id = None, template_name='madman/info/type.html'):
    mediatype = get_object_or_404(MediaType, pk=id)  
    return render( request, template_name, locals() ) 

@login_required
def mediafile(request, id=None):
    f = get_object_or_404(MediaFile, pk=id)
    size = f.get_size()
    dump = str(request)
    return render_to_response(
        'madman/info/file.html', 
        {
            'file': f, 
            'file_size': size, 
            'dump' : dump, 
        },
        context_instance = RequestContext(request), 
    )

@login_required
def medialocation(request, id=None):
    location = MediaLocation.objects.get(pk=id)
    files = MediaFile.objects.filter(location=location).order_by('name')
    locations = MediaLocation.objects.filter(parent=id).order_by('name')

    #build files in location pagniation
    filepaginator = Paginator(files, 10)
    try:
        filepage = int(request.GET.get('filepage', '1'))
    except ValueError:
        filepage = 1
    # If page request (9999) is out of range, deliver last page 
    try:
        paginatedFileList = filepaginator.page(filepage)
    except (EmptyPage, InvalidPage):
        paginatedFileList = filepaginator.page(filepaginator.num_pages)    
    #build locations in location pagniation 
    locationpaginator = Paginator(locations, 10)
    # Make sure page request is an int. If not, deliver first page.
    try:
        locationpage = int(request.GET.get('locationpage', '1'))
    except ValueError:
        locationpage = 1
    # If page request (9999) is out of range, deliver last page 
    try:
        paginatedLocationList = locationpaginator.page(locationpage)
    except (EmptyPage, InvalidPage):
        paginatedLocationList = locationpaginator.page(locationpaginator.num_pages)    
    return render(request, 'madman/info/location.html', locals() ) 

def report( request ):
    report = {} 
    report['Total Size'] = 0 
    report['Location Count'] = MediaLocation.objects.count() 
    report['File Count'] = MediaFile.objects.count()  
    return render(request, 'madman/report.html', locals() )

@login_required
def template(request, template_type=None):
    if template_type:
        return render(request, "madman/%s.html" % template_type, locals() ) 
    else:
        return render(request, "madman/base.html", locals() ) 


