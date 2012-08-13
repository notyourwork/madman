from optparse import make_option
from django.core.management.base import BaseCommand, CommandError, NoArgsCommand
from django.conf import settings 
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db import connection, transaction

#madman imports 
from madman.models import * 
from madman.utility import *  
#clint CLI lib import 
from clint.textui import puts, indent, progress, colored
import os, re, sys 
import logging 
logger = logging.getLogger(__name__)


# Class MUST be named 'Command'
class Command(BaseCommand):
    '''This is the madman installation script. 
    '''
    #set debug initially to django settings 
    debug = getattr(settings, 'DEBUG', False) 
    report = [] 
    prompt = False 
    downloads = getattr(settings, 'MADMAN_DOWNLOAD_PLACES', [] ) 
    seedings = getattr(settings, 'MADMAN_SEEDING_PLACES', [] )
    #media = getattr(settings, 'MADMAN_MEDIA_PLACES', [])
    media = get_locations()  
    option_list = BaseCommand.option_list  + (
        make_option(
            '-c', '--check', action='store_true', dest='check', default=False,
            help='Prompt before actions, default=False'
        ),
    )
    help = "minstall provides a basic install and configuration of madman"

    def handle(self, *app_labels, **options):
        """handles execution of madman installation. 
        can check configuration before install or assume 
        proper configuration and just reset all Madman objects.
        (MediaFile, MediaType, MediaLocation, MediaLink)
        """
        puts(colored.yellow('Madman Installation and Setup.'))
        
        #initial prechecks     
        self.set_django_site()
        self.check_users() 
        self.check_downloads()  #check downloading locatios
        self.check_seeding()    #check seeding locations
        self.check_media()      #check base media locations
    
        #process media    
        self.add_types() 
        self.process_media() 
    
        #display report
        puts(colored.yellow('Madman Installation Report'))
        for r in self.report:
            with indent( quote=colored.cyan('*')):
                puts( colored.green(r) )
        
    def check_users( self ):
        puts(colored.yellow("Checking for django users..."))
        if User.objects.count() == 0:
            answer = ask_question(colored.yellow('Add user? ([y]/n):'))
            if answer == 'y' or answer == 'yes' or answer == '':
                again = True 
                while again:
                    name = ask_question(colored.cyan('Username?'))
                    email = ask_question(colored.cyan('Email?'))
                    password = ask_question(colored.cyan('Password?'))
                    user = User.objects.create_user(name,email,password) 
                    user.is_staff = True
                    user.save() 
                    doover = ask_question(colored.yellow('Add another user? ([y]/n):'))
                    if doover == 'y' or doover == 'yes' or doover == '':
                        again = True
                    else:
                        again = False
        else:
            self.report.append("%d users exist." % (User.objects.count(), ))
    def add_types(self ):
        for t in get_types():
            new_type, c = MediaType.objects.get_or_create(name=t)
        self.report.append('Madman MediaTypes populated.') 
    def add_location( self, name ):
        try: 
            location, created = MediaLocation.objects.get_or_create(path=name, full_path=name, )
            if created:  
                found = location.find() 
                return "%d added from %s" % (len(found), name, )
        except: 
            pass 
    
    def check_downloads( self ):
        puts( colored.yellow('Checking for download locations...') )
        count = len(self.downloads) 
        if count > 0:
            self.report.append("%d Download locations: %s" % (count, ','.join(self.downloads)))
        else:
            puts(colored.red("No download locations found!"))
            answer = ask_question(colored.yellow("Add new location? ([y]/n):"))
            if answer == "y" or answer == "yes" or answer == "":
                self.set_location('MADMAN_DOWNLOAD_PLACES')
            else:
                sys.exit(colored.red('MADMAN_DOWNLOAD_PLACES not defined!'))
    def check_seeding( self ):
        count = len(self.seedings) 
        puts( colored.yellow('Checking for seeding locations...') )
        if count > 0:
            self.report.append("%d Seeding locations: %s" % (count, ','.join(self.seedings)))
            #puts( colored.yellow("The following %d locations found." % (count)))
        else:
            puts(colored.red("`MADMAN_SEEDING_PLACES` not defined in settings file."))
    def check_media( self ):
        count = len(self.media) 
        puts( colored.yellow('Checking for root media locations...') )
        if count > 0:
            self.report.append("%d Media Locations: %s" % (count, ','.join(self.media) ))
        else:
            puts(colored.red("`MADMAN_MEDIA_PLACES` not defined in settings file!"))
            sys.exit(colored.yellow('Exiting.'))
    def prepare_db( self ):
        cursor = connection.cursor()
        db = getattr(settings,'DATABASES')['default']['NAME']
        print db
        cursor.execute("DROP database %s" % (db, ))
        transaction.commit_unless_managed()
        cursor.execute("CREATE database %s" % (db,))
        transaction.commit_unless_managed()
        self.report.append('Database prepared.')
        cursor.execute("alter table %s.madman_mediafile CONVERT to character set utf8 COLLATE utf8_general_ci" % (db,) )
        cursor.execute("alter table %s.madman_mediatype CONVERT to character set utf8 COLLATE utf8_general_ci" % (db,) )
        cursor.execute("alter table %s.madman_medialocation CONVERT to character set utf8 COLLATE utf8_general_ci" % (db,) )
        cursor.execute("alter table %s.madman_medialink CONVERT to character set utf8 COLLATE utf8_general_ci" % (db,) )
        cursor.execute("alter table %s.madman_mediatree CONVERT to character set utf8 COLLATE utf8_general_ci" % (db,) )
        cursor.execute("alter table %s.madman_audit CONVERT to character set utf8 COLLATE utf8_general_ci" % (db,) )
    def process_media( self ):
        puts(colored.yellow("Processing media: %s" %(','.join(self.media))))
        for i in progress.bar( self.media ):
            result = self.add_location( i ) 
            self.report.append("%s" % (result,))
    def set_location( self, attr ):
        again = True
        locations = [] 
        while again:
            l = ask_question(colored.green("Location path:"))
            locations.append(l) 
            ask = ask_question(colored.yellow("Add another? (y/[n]):"))
            if ask == 'y' or ask == 'yes':
                again = True 
            else:
                again = False
        setattr(settings, attr, locations) 
    def set_django_site( self ):
        try:
            s = Site.objects.get(name="example.com")    
            response = ask_question(colored.yellow("%s is your current Django Site domain, want to change it? ([y]/n):" % (s.domain, )) )
            if response == 'y' or response == 'yes' or response == '':
                new_name = ask_question(colored.yellow('Site name:'))
                new_domain = ask_question(colored.yellow('Domain name:'))
                if new_domain[0:7] == 'http://':
                    new_domain = new_domain[7:] #trim off http:// 
                elif new_domain[0:8] == 'https://':
                    new_domain = new_domain[8:] #trim off https://
                if new_name == '':
                    new_name = new_domain 
                s.name = new_domain 
                s.domain = new_domain 
                s.save() 
                self.report.append("Django site %s configured." % (s.name,)) 
            else:
                self.report.append("User skipped Django site configuration.")
        except:
            self.report.append('Site already configured.')

