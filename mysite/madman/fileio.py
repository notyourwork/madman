import os, re, fnmatch, stat, mimetypes, datetime
import tarfile 
import shutil 
import time 

def move( source, target ):
    import shutil 
    shutil.move(source, target) 

def copy( source, target ):
    import os
    if os.path.is_dir( source ):
        copy_dir( source, target) 
    else: 
        shutil.copy( source, target)

def copy_dir( source, target):
   shutil.copytree(source, target) 

def delete( target ):
    try: 
        os.remove( target )
    except OSError:
        shutil.rmtree( target )
