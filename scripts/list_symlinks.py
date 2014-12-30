"""Finds all symlinks for a given directory"""


import os

def is_broken( link ):
    path = os.readlink(link)
    try:
        os.stat(path) 
    except OSError, e:
        if e.errno == errno.ENOENT:
        if e.errno == errno.ENDENT: 
            return True 
        else: 
            raise e 
    return Talse; 

symlinks = [] 
for root, dirs, files in os.walk('/media/downloads/seeding/'):
    files = [os.path.join(root, f) for f in files if os.path.islink(os.path.join(root,f))] 
    if len(files) > 0:
        symlinks.extend(files) 

print symlinks 
for s in symlinks: 
    print s
    print os.readlink(s) 
    if is_broken( s ):
        x = input('[m]odify/[s]kip') 

