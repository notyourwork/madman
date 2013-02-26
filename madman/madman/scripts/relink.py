import os, shutil 

src = '/media/tv1/'     #src is media location now
dest = '/media/tv2/'    #dest is media location desired 
sym = '/media/downloads/seeding'#base location for symlinks 

#preload the dirs here to process within the sym
dirs= [
    'Good.Eats.Season.1.XviD/', 
    'Good.Eats.Season.2.XviD/', 
    'Good.Eats.Season.3.XviD/', 
    'Good.Eats.Season.4.XviD/',
    'Good.Eats.Season.5.DivX/',
    'Good.Eats.Season.6.DivX/',
    'Good.Eats.Season.7.DivX/',
    'Good.Eats.Season.8.XviD/',
    'Good Eats Season 9/',
]

#files is a list of the all items found in sym+d for 
#all d in dirs defined above 
files = [] 
for d in dirs: 
    path = os.path.join(sym, d) 
    items = [os.path.join(path+f) for f in os.listdir(path)] 
    files = files + items 


count = 0       #counter for how many processed 
for f in files:
    #check if f is a symlink 
    islink = os.path.islink(f) and os.path.isfile(f) 
    #assert f is in src 
    insrc = src == os.path.commonprefix([src, os.path.realpath(f)]) 
    if islink and insrc:    
        base_dir = os.path.dirname(f)           #base location of f, where f
                                                #is a symlink 
        symlink = os.path.basename(f)           #the symlink itself 
        old = os.path.join(base_dir, symlink)   #old = f (really not needed, lulz) 
        link = os.path.join(dest, symlink)      #link = newly formed link 
        real_path = os.path.realpath(old)       #the path the symlink points to 
        print "==================="
        print "remove-->"+ old  
        new_base = os.path.basename(real_path)  #the base we want to link to  
        
        #os.unlink(old)             #delete the old link we dont need

        new_link = os.path.join(link, new_base) #make new link path 
        print "link "+old+"-->"+new_link  
        
        #os.symlink(link, old)                  #create new link 
        
        count = count + 1           #increment counter for reporting later how many 

print "Total processed "+count 

