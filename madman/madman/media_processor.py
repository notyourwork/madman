import os 
from django.conf import settings 

def movie_processor(path, symlink=None):
    #processes movies and adjusts any symlinks 
    #symlink argument defaults to none in which case 
    #path argument is moved to appropriate location
    #
    #if symlink is passed in, we will adjust symlink
    #after move is made 
    from madman import utility 
    config = getattr(settings, 'MADMAN_MEDIA_CONFIG', {})
    movie = os.path.basename(path) 
    type_choices =  filter(lambda i: type(i) == type(()), config['hd movies'])  
    new_path = utility.get_new_location( movie, type_choices)
    new_full_path = os.path.join(new_path, movie)
    if not utility.file_exists( new_full_path ):
        if confirm("'%s' --> '%s' ?" % (path, new_full_path) ):
            try: 
                shutil.move(path, new_path)         #move original file to new location 
                if symlink:
                    try:
                        os.remove(symlink)
                        os.symlink(new_full_path, symlink) 
                    except Error, e:
                        print e 
            except shutil.Error, e:
                print "error occured with %s path ignoring" % path
    else:
        print "%s already exists" % new_full_path
 
def music_processor(path):
    #@TODO processor for music 
    print "processed %s" % path 

def tv_processor(path): 
    print "tv processed %s" % path  
