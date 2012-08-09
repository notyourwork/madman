import sys, re, mimetypes
from clint.textui import colored, puts 
from optparse import OptionParser

def get_location(location='default'):
    global location_map 
    try: 
        return location_map[location]['places']
    except KeyError:
        return get_location(location_map['__default'])

def get_def(location):
    global location_map 
    try:
        return location_map[location]["definitions"]
    except KeyError:
        return get_def(location_map["__default"])
    
def is_type(*args, **kwargs):
    '''check is string matches the regular expression
    definition'''
    try: 
        locations = kwargs['location'].split(',')
    except KeyError:
        sys.exit('Exiting no location defined')
    try:
        definition = kwargs['definition']
    except KeyError:
        sys.exit('Exiting no defn found') 
    return definition.match(location)

def process(location, *args, **kwargs):
    global media_definitions 
    print "process(location=%s, **kwargs=%s)" % (location, kwargs, ) 
    for i in media_definitions:
        print media_definitions[i] 
    
def list_media(*args, **kwargs):
    """lists media in defined location""" 
    print "kwargs:",kwargs

def get_function(type=""):
    def gather(sources):
        items = []; sources = []; 
        for s in sources: 
            items = items + [os.path.join(s,l) for l in os.listdir(s)]
        return items 
    def process(places=""):
        return places
    if type == "gather":
        return gather
    elif type == "process":
        return process

function_map = {
    'process':process, 
    'is_type':is_type,
    'list':list_media, 
}
