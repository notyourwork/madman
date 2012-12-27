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
    file_count = 0; dir_count = 0; error_count = 0; ignore_count = 0; link_count = 0;
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
        make_option('-t','--test', dest='test', action='store_true',
            help='Runs as normal but does not actually move/copy anything or add to the db'
        ),
        make_option('-l','--location', dest='location',
            help='Runs the manage command against these locations, a comma separated list of absolute paths'
        ),
        make_option('-s','--symlink', action='store_true', dest='symlink', default=True, 
            help='to symlink the currently processed media or not, that is the question? default is true as we assume we do'
        ),
    )
    help = "[mmanage] --command to manage media in download directories.  for each file found which has not already been processed script will try to classify and then process.  \n\tClassification means associating this media file or media location with an associated MediaType.  \n\tupon proper classification script will then modify the file system to relocate the file or location (and locations contents) to the appropriate place.  "

    def handle(self, *app_labels, **options):
        self.prompt = options['prompt']
        self.test = options['test']
        if self.test:
            print "Starting up test mode, no actions will be taken" 
        self.debug = options['debug']
        if self.debug:
            print "Debugging is enabled!"
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
            question = colored.yellow("Do you want to process the following %d locations: %s" % (len(self.locations), self.locations, ))
            if not confirm(question, True): 
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
        print "process_item - %s" % name
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
            self.ignore_count += 1 

    def process_dir( self, name ):
        #need to link it up with its parent when created here...
        #since directories wont get copied/moved, this is ok
        exists = MediaLocation.objects.filter(name=name).exists()
        if not exists:
            if self.debug:
                print "processing dir"
            #can you say ghetto?
            tmplocations = self.locations
            self.locations = [name]
            self.process_locations()
            self.locations = tmplocations
            if not self.test:
                d, created = MediaLocation.objects.get_or_create( path=name )
            else:
                print "This is where we would add the dir"
        else: 
            if self.debug:
                print "We have already encountered '%s' and are skipping it" % name
            self.ignore_count += 1 
        self.dir_count += 1

    def process_link( self, name ):
        #store a medialink for symlinks found 
        if self.debug:
            print "Found a link: %s" % name
        #I think this is the best way to check if the item exists...
        linklocation, linkname = os.path.split(name)
        exists = MediaLink.objects.filter(name=linkname).exists()
        if not exists:
            filepath = os.readlink(name)
            #send the linked item for processing
            #Do we need to process something that has most likely already been processed?
            #self.process_item(filepath)
            if not self.test:
                #@TODO find mediafile it points to or create it
                medialink, created = MediaLink.objects.get_or_create(name=name, comments=name)
                if created:
                    #It will be there because we just processed it
                    filelocation, linkpointsto = os.path.split(filepath) 
                    f, created = MediaFile.objects.get_or_create(name=linkpointsto)
                    if self.debug:
                         print "processing link" 
        
                    #won't need these because we can just follow the linked object for info
                    #d.classify() 
                    #d.process()
                    medialink.mediafile = f
                    medialink.save()
                    self.link_count += 1
            else:
                print "Test mode means we stop here before we send the link to be saved"
        else: 
            if self.debug:
                print "We have already encountered '%s' and are skipping it" % name
            self.ignore_count += 1 
 
    def process_file( self, name ): 
        #try to get object from database by its base name 
        #need to use a .is_created function since whatever file is here will get processed and no longer exist
        exists = MediaFile.objects.filter(name=name).exists()
        if not exists:
            istv = re.search(r"S([0-9]+)E([0-9]+)", name, re.I)
            if istv:
                if self.debug:
                    print "Found a tv show: %s for season: %s, episode %s" % (name, istv.group(1), istv.group(2))
            else:
                if self.debug:
                    print "Found something that is not a tv show %s" % name
            if not self.test:
                f, created = MediaFile.objects.get_or_create( name=name )
                if created:
                    #What is this?
                    from utility import process_file 
                    if process_file( name ):
                        self.file_count += 1 
                    else:   
                        logger.error("file:%s" % (name,) )
                else: 
                    self.ignore_count += 1
            else:
                print "This is where we would process if we weren't in test mode"
        else: 
            if self.debug:
                print "We have already encountered '%s' and are skipping it" % name
            self.ignore_count += 1 

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
                if self.prompt:
                    #This needs to be moved so that already seen items arent asked to be processed
                    if confirm(colored.red("%d/%d process %s" % (count, len(contents_of_base), item,)),  True): 
                        self.process_item( item, base ) 
                    else:
                        if self.debug:
                            print colored.yellow("Not processing 'cuz ya said No")
                        #Not setting this so we can manually iterate as long as we want
                        #self.ignore_count += 1
                    count += 1 
                else:
                    self.process_item( item, base )
