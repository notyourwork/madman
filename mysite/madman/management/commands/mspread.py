from optparse import make_option
from optparse import OptionParser
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings 
from madman.models import * 
from madman.utility import *
import os
import re  
import types 
import shutil

import logging 
logger = logging.getLogger(__name__)
from clint.textui import progress, colored

# Class MUST be named 'Command'
class Command(BaseCommand):
    """media management spread command, evenly spreads 
    media over hard drives. 
    """
    #counters for reporting post execution 
    file_count = 0; dir_count = 0; error_count = 0; ignore_count = 0; 
    file_list = []; dir_list = []; error_list = []; link_list = []; 
    locations = [] #stores all locations being processed  
    item_count = 0 
    items = []          #stores all items found 
    all_media = {}      #dict of media locations --> items 
    debug = getattr(settings, 'DEBUG', False) 

    # Displayed from 'manage.py help madmanmanage'
    # make_option requires options in optparse format
    option_list = BaseCommand.option_list  + (
        make_option(
            "-l", "--locations",
            action="store",
            dest="locations",
            default='',
            choices=[''].extend( get_locations() ), 
            help="the path to process, default is all locations, choices = %s" % get_locations()   
        ),
        make_option(
            "-t", "--type",
            action="store",
            dest="type",
            default='',
            choices=[''].extend( get_types() ), 
            help='select a type of media to process, types = %s' % get_types() 
        ),
        make_option(
            "-d", "--debug",
            action="store_true", 
            dest="debug",
            help="debugging on or off?",
            default=getattr(settings, 'DEBUG', False), 
        ),
        make_option(
            "-p", "--prompt", 
            action="store_true",
            dest="prompt",
            default=False,
        ),
    )
    help = "[mspread] --command to redistribute all media.  When a new location is added for a given content type we want to shuffle that content type around so media is evenyl dsitributed.\nie. for hd movies if we had /media/hdmovies1 and /media/hdmovies2 and then added /media/hdmovies3\nWe want to shift all media from hdmovies1,2 into 1,2,3.  "

    def handle(self, *app_labels, **options):
        self.prompt = options['prompt']
        if options['debug']: self.debug = True
        
        if options['locations']:
            self.locations = options['locaions'].split(',')  
        else:
            self.locations = get_locations() 
        
        locations = []      #stores all locations being processed
        items = []          #stores all items found 
        all_media = {}      #dict of media locations --> items 
        item_count = self.item_count 
        
        #get all locations from all media 
        for media in getattr(settings, 'MADMAN_MEDIA_CONFIG', {}):
            locations = get_locations(media)  
            for loc in locations:
                items = get_media(loc)
                item_count += len(items)
                try: 
                    all_media[loc].extend(items)  
                except KeyError, e:
                    all_media[loc] = items 
            print "Searching content type: %s [%d locations with %d items]" % (media, len(locations), item_count )

        #for all locations and items within check they belong 
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

    def confirm_locations( self ):
        '''confirms with user the locations to process by
        iterating over them if user choses to do so'''
        new_locations = [] 
        if self.prompt: 
            answer = ask_question("Do you want to process the following %d locations: %s\n(yes/no):" % (len(self.locations), self.locations, )) 
            if answer != 'yes' and answer != 'y' and answer != True:
                for loc in self.locations:
                    answer = ask_question("Do you want to process %s (yes/no):" % (loc,)) 
                    if answer == 'yes' or answer == 'y':
                        new_locations.append(loc) 
                if len(new_locations) > 0:
                    self.locations = new_locations
                    print "Processing user specified locations."
                else:
                    import sys
                    sys.exit("User cancelled, no locations to process. Exiting.")
            else:
                print "Processing default locations defined in settings."
        else:
            return True

    def process_item( self, item, base=None ): 
        '''processes the given item, if base != none will prepend to 
        item if absolute path is needed, if base == none assumes item
        is absolute path or we are in cwd relative to item so we wouldnt
        need it :) '''
        #get absolute path for item 
        if base != None: 
            name = os.path.join(base, item )
        else:
            name = item 
        #check what type of item this is and process accordingly 
        if os.path.isfile( name ):
            if os.path.islink( name ):
                #store a medialink for symlinks found 
                medialink, created = MediaLink.objects.get_or_create(name=item, comments=name)
                #@TODO find mediafile it points to or create it
                filepath = os.readlink(name) 
                filelocation, linkpointsto = os.path.split(filepath) 
                f, created = MediaFile.objects.get_or_create(name=linkpointsto)
                medialink.mediafile = f
                medialink.save() 
            else:
                #try to get object from database by its base name 
                f, created = MediaFile.objects.get_or_create( name=item )
                if created:
                    f.classify()
                    f.process() 
                    from utility import process_file 
                    if process_file( name ):
                        self.file_count = self.file_count+1 
                    else:   
                        logger.error("file:%s" % (name,) )
                else: 
                    self.ignore_count = self.ignore_count + 1
        elif os.path.isdir( name ):
            #need to link it up with its parent when created here... 
            d, created = MediaLocation.objects.get_or_create( name=item )
            if created:
                d.classify() 
                d.process() 
                from utility import process_dir
                if process_dir( name ):
                    self.dir_count = self.dir_count+1
            else: 
                self.ignore_count = self.ignore_count+1 
            self.dir_count = self.dir_count+1
        else:
            self.ignore_count = self.ignore_count+1 

    def process_locations( self): 
        dirs = {}
        for l in self.locations:
            dirs[l] = os.listdir( l )
        it = iter( dirs.items() )
        for d in it:
            base = d[0]
            contents_of_base = d[1] 
            os.chdir( base )    #change to this directory 
                                # in case we want to work relatively
            for item in progress.bar( contents_of_base ):
                answer = ask_question("Do you want to process %s (yes/no):" % (item,) )
                if answer == 'yes' or answer == 'y':
                    self.process_item( item, base ) 
                else:
                    self.ignore_count = self.ignore_count+1


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


