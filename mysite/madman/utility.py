from django.db import models
from django.conf import settings 
from clint.textui import * 
import os
import shutil
import re
import fnmatch
import stat
import mimetypes
from functools import wraps
from time import time
import datetime 
import types 
from optparse import OptionParser

import logging 
logger = logging.getLogger(__name__)


def ask_question( question ):
    ''' assumes CLI, prompts user for input and returns answer''' 
    return raw_input( "%s" % (question, ) )

def ask_boolean( question, true_values = ['y','yes'], false_values = ['n','no'], default=False ):
    '''function ask_boolean prompts user for input 
    by presenting input arg question to user
    -accepts additional input: 
        true_values list
        false_value list 
    for custom affirmation values. 
    -if user responds to input question with a value
    in input argument true_values function returns true
    -otherwise returns default if defined, or false 
    likewise for false_values we would return false.  
    additionally, if user responds with a value not in
    '''
    user_response = ask_question( question )
    try:
        if true_values.index(user_response):
            response = True 
        elif false_values.index(user_response):
            response = False 
        else:
            response = default 
    except ValueError:
        response = False 
    
def get_dir_size( start_path=None ):
    """
        recursively calculate a directory size
        input - starting directory path (assumes absolute) 
        output - a number of bytes  0 or greater that is the 
        size of the directory, in worst case with errors, 
        issues 0 is returned 
    """
    total = 0 
    if start_path:
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                try:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink( fp ): 
                        total = total + os.path.getsize( fp )
                except:
                    msg = "problem getting size of %s" % (fp)
                    logger.error(msg )
    return total

def humanize_bytes( bytes ):
    '''convert a byte quantity to a human readable format'''    
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

def get_classification_dict( ):
    #get a compiled list of all media defintions
    from madman.models import MediaType 
    types = dict()
    for t in MediaType.objects.all():
        types[t.name] = re.compile( t.definition )
    return types 

def test_media( definition=None, value=None ):
    """ 
        tests a media piece against a given definition 
        input - a string defining a regex to test against 
        output - true if match, false otherwise 
    """
    test = re.compile( definition )
    return test.match(value)

def get_size( path ):
    """ returns size for a given path"""
    try: 
        return os.path.getsize( path )
    except OSError:
        return 0
       
def in_downloading( name ):
    """returns true if input is a downloading 
    location, false otherwise"""
    locations = getattr(settings, 'MADMAN_DOWNLOAD_LOCATIONS', [] )
    for l in locations: 
        if l == name[0:len(i)]:
            return True 
    return False

def in_seeding( name ):
    """returns true if input is a seeding location
    false otherwise"""
    locations = getattr(settings, 'MADMAN_SEEDING_LOCATIONS', [] )
    for l in locations: 
        if l == name[0:len(i)]:
            return True 
    return False

def classify_media( name ):
    '''returns MediaType for a given input, 
    input is  if input is (file or directory)
      and determines what it is, movie, '''
    from madman.models import MediaType
    types = dict() 
    for t in MediaType.objects.all():
        types[t.name] = re.compile( t.definition )
    return name 

def flush_madman_media( ):
    puts(colored.yellow('Deleting Media Types, Locations, Files and Links from Madman'))
    MediaType.objects.all().delete() 
    MediaLocation.objects.all().delete()
    MediaFile.objects.all().delete()
    MediaLink.objects.all().delete() 

def timed(fn):
    '''timing decorate to time exeuction 
    time for a given function.  
    usage: 
        @timed 
        def function():
            ...
        
        function() #will be timed when called 
    '''
    def wrapper(*args, **kwargs):
        print("calling %s(%s,%s)"%(fn.__name__,args, kwargs))
        start = time() 
        result = fn(*args, **kwargs)
        total = time() - start
        print("%s --> %s"%(fn.func_name,result))
        print "%s took %d time to finish" % (fn.__name__, total)
        logger.info( '%s took %0.3f ms' % (fn.__name__, total ))
        return result 
    wrapper.func_name = fn.func_name
    return wrapper 

def timed2(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time()
        result = f(*args, **kwds)
        elapsed = time() - start
        print "%s took %d time to finish" % (f.__name__, elapsed)
        return result
    return wrapper

def get_media(location):
    #returns a list of media items 
    #found in given location 
    #nothing special here, uses os.listdir and removes 
    #"." and "lost+found" directories from list  
    try: 
        os.chdir( location )
        items = os.listdir( os.getcwd() )
        items = filter(lambda i: not i.startswith('.') and i != 'lost+found', items)
        #items = [i for i in items if not i.startswith('.')] 
        return items 
    except OSError, e: 
        print e 

def file_exists( path ):
    #checks if path is an existing file
    #and returns value 
    if os.path.isfile( path ):
        try:
            with open(path ) as f: 
                return True 
        except IOError as e:
            return False 
    return False 

def find_symlink(path):
    #input expects an absolute path, 
    #checks all symlinks for a match 
    #
    #@TODO may want to consider handling multiple
    #symlinks to same file for situations where you are seeding
    #a media item on mutliple trackers so you have > 1 symlink
    #for a media item.  
    #
    #proposed solution: return a list 
    
    for link in get_all_symlinks():
        if path == os.path.realpath(link):
            return link  

def get_all_symlinks(location=None):
    #searches base folder recursively for all symlinks within
    #returns this list 
    if location == None:
        location = '/media/downloads/seeding/'
    symlinks = [] 
    for root, dirs, files in os.walk( location ):
        files = [os.path.join(root, f) for f in files if os.path.islink(os.path.join(root,f))] 
        if len(files) > 0:
            symlinks.extend(files) 
    return symlinks 
 
def get_new_location(path, choices):
    #returns correct base location for given path.
    #path is absolute path to a given media item,
    #choices is a tuple of tuples of the form:
    #   choices = (
    #        ('/media/hdmovies1', "[0-9A-E]"), 
    #        ('/media/hdmovies2', '[F-L]'), 
    #        ('/media/hdmovies3', '[M-R]'), 
    #        ('/media/hdmovies4', '[S-Z]'), 
    #    ),
    #
    #so we iterate over choices, and check the reg_ex 
    #for a match.      
    media_name = os.path.basename(path) 
    for base_path, reg_ex_defn in choices:
        reg_ex = re.compile(r"%s" % (reg_ex_defn), re.IGNORECASE)  
        if is_located(media_name, reg_ex):
            return base_path 

def is_located(path, reg_ex):
    #takes an absolute or relative path and checks if
    #reg_ex is a match.  
    #we also handle the situaiton where we ignore "The " for things like
    #a movie named "The Green Mile" that should be located in the 
    #"g" section, not the "t" section.  
    media_name = os.path.basename(path) 
    test = False 
    if media_name.startswith('The ') :
        #media starts with The, ignore and process
        #rest of the string 
        test = reg_ex.match( media_name[4:] )
    else:
        test = reg_ex.match( media_name ) 
    return test 

def get_processor( media_type ):
    #returns a processor function for a given type of media
    #defined in the global config.  
    #we do this by filtering all attributes of a config media type
    #and return the function.  
    #
    #ie: 
    #'hdmovies' : (
    #        movie_processor, 
    #        ('/media/hdmovies1', "[0-9A-E]"), 
    #        ('/media/hdmovies2', '[F-L]'), 
    #        ('/media/hdmovies3', '[M-R]'), 
    #        ('/media/hdmovies4', '[S-Z]'), 
    #    ),
    #for media_type = "hdmovies" we would return the reference to 
    #movie_processor function. 
    config = getattr(settings, 'MADMAN_MEDIA_CONFIG', {})
    try:
        return filter(
            lambda f: isinstance(f, (types.FunctionType, types.BuiltinFunctionType)), 
            config[media_type]
        )[0] 
    except KeyError, e:
        print e 
     
def get_location_processor( location ):
    #returns a processor function for a given
    #location. Similar to get_processor but instead accepts
    #a media location and works backwards from that.  
    #'hdmovies' : (
    #       movie_processor, 
    #        ('/media/hdmovies1', "[0-9A-E]"), 
    #        ('/media/hdmovies2', '[F-L]'), 
    #        ('/media/hdmovies3', '[M-R]'), 
    #        ('/media/hdmovies4', '[S-Z]'), 
    #    ),
    #
    #if location = "/media/hdmovies1" 
    #we would return "movie_processor.  
    config = getattr(settings, 'MADMAN_MEDIA_CONFIG', {})
    media_type = '' 
    for key in config:
        items = filter(lambda i: type(i) == type(()), config[key])  
        for item in items:
            if location == item[0]:
                return get_processor( key )

def get_config_locations( media_type=None ):
    #@TODO try except KeyError on config dict 
    try:
        config = getattr(settings, 'MADMAN_MEDIA_CONFIG', []) 
        locations = []
        if media_type: 
            media_def = filter(lambda i: type(i) == type(()) , config[media_type])
            for location, regex in media_def:
                locations.append(location) 
        else:
            for key in config:
                media_def = filter(lambda i: type(i) == type(()) , config[key])
                for location, regex in media_def:
                    locations.append(location) 
        return locations
    except KeyError, e:
        print e 

def get_download_locations( ):
    return getattr(settings, 'MADMAN_DOWNLOAD_PLACES', []) 
    
def get_locations( media_type=None ):
    try:
        config = getattr(settings, 'MADMAN_MEDIA_CONFIG', []) 
        locations = []
        if media_type: 
            media_def = filter(lambda i: type(i) == type(()) , config[media_type])
            for location, regex in media_def:
                locations.append(location) 
        else:
            for key in config:
                media_def = filter(lambda i: type(i) == type(()) , config[key])
                for location, regex in media_def:
                    locations.append(location) 
        return locations
    except KeyError, e:
        print e 

def get_re( location ):
    config = getattr(settings, 'MADMAN_MEDIA_CONFIG', {})
    for media_type in config:
        locations = filter(lambda i: type(i) == type(()) , config[media_type])
        for l, reg_ex in locations:
            if location == l:
                return re.compile(r"%s" % (reg_ex), re.IGNORECASE)  

def get_types( ):
    #@TODO try except KeyError on config dict 
    config = getattr(settings, 'MADMAN_MEDIA_CONFIG', []) 
    return [m for m in config] 

def get_type( location ):
    config = getattr(settings, 'MADMAN_MEDIA_CONFIG', [])
    for key in config:
        if location in get_locations(key):
            from madman.models import MediaType
            try: 
                media_type = MediaType.objects.get(name=key)
            except MediaType.DoesNotExist, e:
                media_type = None  
            return media_type 
        else:
            pass 
    return None 
 
def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False
