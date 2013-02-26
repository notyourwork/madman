from django.db import models
from madman.models import *
from django.conf import settings 
from clint.textui import * 
import os
import shutil
import re
import fnmatch
import stat
import mimetypes
import tarfile, shutil 
from functools import wraps
import zipfile 
import UnRAR2

def process_tar( name ):
    '''open tarfile and process contents accordingly
    function assumes name is a absolute path to a file 
    which is a tarfile
    '''
    debug = getattr(settings, 'DEBUG', False) 
    if debug: 
        print "untar %s " % (name, ) 
    else: 
        tarball = tarfile.open( name )
        tarball.extractall()
    return True 

def process_rar( name ): 
    '''rar is a bastard of a area... there isnt a
    tried and true library for extracting a rar 
    archive.  We must rely on system calls 
    '''
    try: 
        rar = UnRAR2.RarFile('test.rar')
        rar.extract()
         
    except FileOpenError: 
        return "unable to open file "+name    

def process_zip( name, dest ):
    '''extract a zip archive'''
    return name 

