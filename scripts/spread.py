import os
import shutil
import re 
import types 
from optparse import OptionParser
import logging 

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

def get_all_symlinks():
    #searches base folder recursively for all symlinks within
    #returns this list 
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

def main():
    #the main guy, doing all the work.  
    #1. find all items in all types of media 
    #2.  
    parser = get_parser()  
    (options, args) = parser.parse_args()

    locations = [] 
    items = [] 
    all_media = {} 
    item_count = 0 
    #iterate over config and get media locations
    #and then iterate over locations to get all items
    #in location 
    
    for media in config:
        locations = get_locations(media)  
        for loc in locations:
            items = get_media(loc)
            item_count += len(items)
            try: 
                all_media[loc].extend(items)  
            except KeyError, e:
                all_media[loc] = items 
        print "Searching content type: %s [%d locations with %d items]" % (media, len(locations), item_count )

    #for all locations and items within we want to check they belong 
    wrong_location = [] 
    for location in all_media:
        print " -processing %s" % location 
        items = sorted(all_media[location] )
        reg_ex = get_re( location )
        for item in items:
            full_path = os.path.join(location, item) 
            if not is_located( full_path, reg_ex ):    
                wrong_location.append(full_path) 
                print " ->%s" % item  
    
    print "---------------------------------------------"
    #for all media in wrong location, we want to run processor 
    wrong_location = sorted(wrong_location)             
    print "Found %d incorrectly located media items" % len(wrong_location) 
    for item in wrong_location:
        print " -%s "  % item
        f = get_location_processor( os.path.dirname( item ) )
        link = find_symlink( item )  
        if link:
            print " --> linked %s" % (link, ) 
            f(item, link)
        else:
            print " --X unlinked, can safely be moved "   
            f(item)

def movie_processor(path, symlink=None):
    #processes movies and adjusts any symlinks 
    #symlink argument defaults to none in which case 
    #path argument is moved to appropriate location
    #
    #if symlink is passed in, we will adjust symlink
    #after move is made 
    movie = os.path.basename(path) 
    type_choices =  filter(lambda i: type(i) == type(()), config['hdmovies'])  
    new_path = get_new_location( movie, type_choices)
    new_full_path = os.path.join(new_path, movie)
    if not file_exists( new_full_path ):
        if confirm("'%s' --> '%s' ?" % (path, new_full_path) ):
            try: 
                shutil.move(path, new_path)         #move original file to new location 
                if symlink:
                    try:
                        os.remove(symlink)
                        os.symlink(new_full_path, symlink) 
                    except Error, e:
                        print e 
            except shutil.Error, e:
                print "error occured with %s path ignoring" % path
    else:
        print "%s already exists" % new_full_path
 
def music_processor(path):
    #@TODO processor for music 
    print "processed %s" % path 

def tv_processor(path): 
    print "tv processed %s" % path  

def load_config():
    #initialize the global config 
    #with media types, locations and definitions 
    global config
    config  = {
        'hdmovies' : (
            movie_processor, 
            ('/media/hdmovies1', "[0-9A-E]"), 
            ('/media/hdmovies2', '[F-L]'), 
            ('/media/hdmovies3', '[M-R]'), 
            ('/media/hdmovies4', '[S-Z]'), 
        ),
        #'movies' : (
        #    movie_processor, 
        #    ('/media/movies1', '[(0-9A-Z]'), 
        #), 
        #'tv' : (
        #    tv_processor, 
        #    ('/media/tv1/', '[0-9A-J]' ), 
        #    ('/media/tv2', '[K-Z]' ),  
        #),
        #'hdtv' : (
        #    tv_processor, 
        #    ('/media/hdtv1','[0-9A-H]' ),
        #    ('/media/hdtv2','[I-Q]' ),
        #    ('/media/hdtv3', '[R-S]' ),
        #),
        #'music' : (
        #    ('/media/music1/', '[0-9A-G]' ),
        #)
    }
    
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
    media_type = '' 
    for key in config:
        items = filter(lambda i: type(i) == type(()), config[key])  
        for item in items:
            if location == item[0]:
                return get_processor( key )

def get_locations( media_type=None ):
    #@TODO try except KeyError on config dict 
    try:
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
    for media_type in config:
        locations = filter(lambda i: type(i) == type(()) , config[media_type])
        for l, reg_ex in locations:
            if location == l:
                return re.compile(r"%s" % (reg_ex), re.IGNORECASE)  

def get_parser():
    parser = OptionParser(
        usage="usage: %prog [options] filename",
        version="%prog 1.0"
    )
    parser.add_option(
        "-p", "--path",
        action="store",
        dest="path",
        default='',
        choices=[''].extend( get_locations() ), 
        help="the path to process, default is all locations"  
    )
    #parser.add_option(
    #    "-t", "--type",
    #    action="store",
    #    dest="type",
    #    default='',
    #    choices=get_locations(), 
    #    help='select a type of media to process'
    #)
    parser.add_option(
        "-d", "--debug",
        action="callback", 
        callback=set_debugging,
        dest="debug",
        help="debugging on or off?"
    )
    return parser 

def set_debugging(option, opt_str, value, parser):
    logging.basicConfig(level=logging.DEBUG)

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
if __name__ == "__main__":
    load_config() 
    main() 
