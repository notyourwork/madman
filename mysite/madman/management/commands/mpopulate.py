from django.core.management.base import BaseCommand, CommandError
from madman.models import *  
from django.conf import settings 
from madman.utility import * 
import time 
from optparse import make_option
from clint.textui import progress 

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--verbose', action='store_true', dest='verbose',
            help=''),
    )

    help = 'Populates media database for all currently defined parent locations.'
    
    user_continue = True        #boolean for user prompt interaction 
    time_start = time.time()    #start of execution for tracking execution time 
    time_report = ''            #string reporting results of execution time

    def handle(self, *args, **options):
        verbose = options.get('delete')
        print "Searching locations..."
        locations = self.get_locations() 
        if len(locations): 
            print "The following %d locations will be scanned for media: %s\n" % (len(locations), ', '.join([l.name for l in locations]), )
            raw_input("Press any key to continue")
            results = [i.find() for i in MediaLocation.objects.all()]
            print "results:"
            print results 
        else:
            response = ask_question('We cannot seem to find any locations, you want to add some? (y/n)')
            if response == 'yes' or response == 'y':
                print "You entered yes, great.  We will proceed as follows:\n\t1. Add Locations\n\t2. Find Media in Locations\n\t3.Show you the results"
                raw_input("Press Enter to continue...")
                self.add_locations() 
            else:
                print 'ok good bye\n' 

        logger.info( 'Execution time: %0.3f ms' % ((time.time()-self.time_start)*1000.0) ) 

        if verbose: 
            print self.time_report

    def add_locations( self ):
        print "Madman Media Locations\n(At anytime enter 'exit' to move on,\nalso note you should not enter a path inside another path you want to define)" 
        users_locations = []
        count = 1 
        while self.user_continue:
            location_name = ask_question("Location %d Name (ie. 'HD Movies' or 'All Music'):" % (count, ) )
            path= ask_question( "Location %d Path:" % (count, ) )
            #can use os.path.isabs( path ) to detrmine if begins with slash 
            while not os.path.isabs( path ):
                path = ask_question ("%s is invalid:" % (path, )) 

            selected_type = self.get_type() 
            m = MediaLocation(name=location_name, path=path, location_type=selected_type)
            m.save() 
            users_locations.append(m) 
            count = count + 1
            response = ask_question('Add another location? (y/n):') 
            if response != 'y' or response != 'yes':
                self.user_continue = False 
        
        for l in users_locations:
            print l 
    def get_locations( self ):
        return [location for location in MediaLocation.objects.filter(parent=None)]
    def get_type( self ):
        response = ask_question("What type is this location? (enter 'help' for a full list of types):")
        if response == 'help':
            for t in MediaType.objects.all(): print "%s"%(t,)  
            return self.get_type() 
            
        m = MediaType.objects.get(name=response)
        return m 

