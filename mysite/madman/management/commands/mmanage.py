from optparse import make_option
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings 
from madman.models import * 
from madman.utility import ask_question, confirm 
import os
import re 
import sys  
import logging 
logger = logging.getLogger(__name__)
from clint.textui import progress, colored, puts

# Class MUST be named 'Command'
class Command(BaseCommand):
    '''This is the madmanmanage command.  It processes all
    contents of settings.py MADMAN_DOWNLOAD_LOCATIONS for 
    files and directories.  
    -If file is found:
        inspect type and determine appropriate action
        archives tar/rar/zip/gzip - need unpacked and reprocessed 
        iso images - classify and move appropriately 
        mp3s - process 
        folder - dpeends on whats inside (see above) 
            - what if we end up with a mixed bag? 
                like a folder with mp3s and mkvs? not sure 
                probably manually classify 
    -If directory is found:
        need to inspect contents to determine action 
        along with processing directory name to guess
        at media type
    -If symlink is found: 
        add symlink if not defined 
    '''
    #counters for reporting post execution 
    file_count = 0; dir_count = 0; error_count = 0; ignore_count = 0; 
    file_list = []; dir_list = []; error_list = []; link_list = []; 
    locations = [] 
    #set debug initially to django settings 
    debug = getattr(settings, 'DEBUG', False) 
    cron = os.isatty(sys.stdout.fileno())

    # Displayed from 'manage.py help madmanmanage'
    # make_option requires options in optparse format
    option_list = BaseCommand.option_list  + (
        make_option('-c','--cron', action='store_true', dest='cron', default=False, 
            help='@TODO running as a cron job, no prompts, just process the current shizzle'
        ),
        make_option('-p', '--prompt', action='store_true', dest='prompt', default=False,
            help='prompt before doing stuff?'
        ),
        make_option('-d', '--debug', action='store_true', dest = 'debug', default=False,
            help='debugging and stuff??'
        ),
        make_option('-t','--test', dest='test',
            help='Runs as normal but does not actually move/copy anything or add to the db'
        ),
        make_option('-l','--location', dest='location',
            help='Runs the manage command against these locations, a comma separated list of absolute paths'
        ),
        make_option('-s','--symlink', action='store_true', dest='symlink', default=True, 
            help='to symlink the currently processed media or not, that is the question? default is true as we assume we do'
        ),
    )
    help = "[mmanage] --command to manage media in download directories.  for each file found which has not already been processed script will try to classify and then process.  \n\tClassification means associated this media file or media location with an associated MediaType.  \n\tupon proper classification script will then modify the file system to relocate the file or location (and locations contents) to the appropriate place.  "

    def handle(self, *app_labels, **options):
        self.prompt = options['prompt']
        if options['debug']:
            self.debug = True 
        if options['location']:
            self.locations = options['location'].split(',')  
        else:
            self.locations = getattr(settings,'MADMAN_DOWNLOAD_PLACES',[])
         
        self.confirm_locations() 
        self.process_locations() 
        print "Results: files:%d dirs:%d errors:%d ignored:%d" % (file_count, dir_count, error_count, ignore_count,) 

    def confirm_locations( self ):
        '''confirms with user the locations to process by
        iterating over them if user choses to do so'''
        print "confirming locations",  self.locations
        new_locations = [] 
        if self.prompt:
            if not confirm(colored.yellow("Do you want to process the following %d locations: %s" % (len(self.locations), self.locations, )), True): 
                sys.exit("User aborted, no locations to process. Exiting.")
    def process_item( self, name, base=None ): 
        """processes the given item, name, 
        -if base != none will prepend to 
        -item to build absolute path
        1. if item is a file 
            -if a symlink 
            -if a physical file 
        2. if item is a directory 
        """
        print "process_item-"
        #get absolute path for item 
        if base != None: 
            name = os.path.join(base, name )
        #check what type of item this is and process accordingly 
        if os.path.isfile( name ):
            if os.path.islink( name ):
                self.process_link( name )
            else:
                self.process_file( name )
        elif os.path.isdir( name ):
            self.process_dir( name )
        else:
            self.ignore_count = self.ignore_count+1 

    def process_dir( self, name ):
        #need to link it up with its parent when created here...
        d, created = MediaLocation.objects.get_or_create( path=name )
        if created:
            print "processing dir" 
            #d.classify() 
            #d.process()
        else: 
            self.ignore_count = self.ignore_count+1 
        self.dir_count = self.dir_count+1

    def process_link( self, name ):
        #store a medialink for symlinks found 
        medialink, created = MediaLink.objects.get_or_create(name=item, comments=name)
        #@TODO find mediafile it points to or create it
        filepath = os.readlink(name) 
        filelocation, linkpointsto = os.path.split(filepath) 
        f, created = MediaFile.objects.get_or_create(name=linkpointsto)
        medialink.mediafile = f
        medialink.save()
 
    def process_file( self, name ): 
                #try to get object from database by its base name 
                f, created = MediaFile.objects.get_or_create( name=name )
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
    
    def process_locations( self ): 
        """for all locations defined, find all
        items within said locations and process
        each item"""
        dirs = {}
        for l in self.locations:
            dirs[l] = os.listdir( l )
        it = iter( dirs.items() )
        for d in it:
            base = d[0]
            contents_of_base = d[1] 
            #for item in progress.bar( contents_of_base ):
            count = 1 
            for item in contents_of_base:
                if confirm(colored.red("%d/%d process %s" % (count, len(contents_of_base), item,)),  True): 
                    self.process_item( item, base ) 
                else:
                    self.ignore_count = self.ignore_count+1
                count = count+1 
