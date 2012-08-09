from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader

def custom_404(request):
    return render_to_response(
        'madman/main.html', 
        {}, 
        context_instance = RequestContext(request) 
    )
def custom_403(request):
    return render_to_response(
        'madman/main.html', 
        {}, 
        context_instance = RequestContext(request) 
    )
def custom_500(request):
    return render_to_response(
        'madman/main.html', 
        {}, 
        context_instance = RequestContext(request) 
    )

