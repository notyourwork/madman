from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse

from django.template import RequestContext, Context, loader
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def login_user(request):
    state = "Lets login before we get too crazy..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You crazy sob, you logged in!"
            else:
                state = "Sorry guy, your account is not active, the site admin probably deleted you for funzies."
        else:
            state = "zomg, username and password did not match, did you forget them?"

    return render_to_response(
        'authentication/auth.html',
        {'state':state, 'username': username},
        context_instance=RequestContext(request),
    )
