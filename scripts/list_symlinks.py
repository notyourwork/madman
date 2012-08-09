"""Finds all symlinks for a given directory"""


import os
symlinks = [] 
for root, dirs, files in os.walk('/media/downloads/seeding/'):
    files = [os.path.join(root, f) for f in files if os.path.islink(os.path.join(root,f))] 
    if len(files) > 0:
        symlinks.extend(files) 

print symlinks 
print len(symlinks) 
