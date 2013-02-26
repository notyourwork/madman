from optparse import make_option
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings 
from madman.models import * 
from madman.utility import get_dir_size, humanize_bytes
import os, re, sys 

import logging 
logger = logging.getLogger(__name__)

# Class MUST be named 'Command'
class Command(BaseCommand):
    default_count = 20 
    defined_count = 0 
    # Displayed from 'manage.py help mycommand'

    # make_option requires options in optparse format
    option_list = BaseCommand.option_list  + (
        make_option('-c', '--count', dest='count', default=default_count,
            help="How many to list? Default = %d" % (default_count,)  
        ),

    )
    help = "Displays largest items in seeding directories that are not processed.  A pseudo report/snapshot of what needs processed that hasn't been."

    def handle(self, *app_labels, **options):
        self.defined_count = options['count'] 
        locations = self.get_locations() 
        date_tuple_list = []; ignore_list = []; dirs = {}
        #get stuff in locations 
        for l in locations:
            dirs[l] = os.listdir( l )
        it = iter( dirs.items() )
        for d in it: 
            base = d[0]
            base_contents = d[1] 
            for i in base_contents:
                this_entry = os.path.join(base, i )
                if os.path.isfile( this_entry ):
                    try: 
                        this_size = os.path.getsize( this_entry )
                    except OSError:
                        ignore_list.append( this_entry ) 
                elif os.path.isdir( this_entry ):
                    this_size = get_dir_size( this_entry )
                else:
                    ignore_list.append( this_entry )
                    this_size = 0 
                date_tuple_list.append( (this_entry, this_size ) )
        
        #sort by second element of tuples (date for dir/file) 
        date_tuple_list.sort(key=lambda x: x[1])
        puts(colored.yellow('The following items are not linked in seeding directory'))
        odd = True; counter = self.defined_count
        for f,t in date_tuple_list[-int(self.defined_count):]:
            to_print = "%d: %s %s" % (counter, humanize_bytes(t), f )
            if odd:
                odd = False
                with indent(4, quote=colored.blue('|')):
                    puts(colored.cyan(to_print))
            else:
                odd = True
                with indent(4, quote=colored.blue('|')):
                    puts(colored.yellow(to_print))
            counter = counter - 1

    def get_locations( self ):
        locations = getattr(settings, 'MADMAN_SEEDING_PLACES', []) 
        if len(locations) == 0:
            answer = ask_question(colored.red("No seeding location defined!  Do you want to add one? ([y]/n):")) 
            if answer != 'yes' and answer != 'y' and answer != '':
                sys.exit('Exiting by request of user') 
            else:
                answer = ask_question(colored.yellow("Location:"))
                locations.append(answer) 
        return locations 

