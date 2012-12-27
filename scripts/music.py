#!/usr/bin/python -tt


"""
Music Processing Script, checks a given folder for files/directories 
and processes each accordingly then moves to final destination.
"""

import sys
import os
import tarfile 

# Define a main() function that prints a little greeting.
def main():
        # Get the name from the command line, using 'World' as a fallback.
        baseLocation = ""
        baseDestination = ""
        if len(sys.argv) >= 2:
                #arguments provided we will want to use 
                baseLocation = sys.argv[1]
                baseDestination = sys.argv[2]
        else:
                baseLocation = "/media/isos1/music/new/"
                baseDestination = "/media/isos1/music/"
                
        getFiles(baseLocation, baseDestination)


# Function accepts one parameter the location to get files
# from and then iterates over this list 
def getFiles(location, destination):
    print "getFiles(): looking in "+location
    dirCount = 0 
    dirTotal = 0 
    dirIgnored = 0 
    fileTotal = 0
    fileCount = 0 
    fileIgnored = 0 
    for dirname, dirnames, filenames in os.walk('.'):
        for subdirname in dirnames:
            #print os.path.join(location, subdirname)
            if subdirname[0:1].isalpha(): 
                fromDir = location+subdirname
                toDir = destination+subdirname[0:1].lower()+'/'+subdirname
                try:
                    os.rename(fromDir, toDir)  
                    print fromDir+ ' --> ' + toDir
                except os.error:
                    print '[error] '+fromDir
                dirCount += 1 
            elif subdirname[0:1].isdigit():
                fromDir = location+subdirname 
                toDir = destination+'#/'+subdirname
                print fromDir+' --> ' + toDir
                os.rename(fromDir, toDir) 
                dirCount += 1
            else:
                print '[uncategorized] '+subdirname 
                dirIgnored += 1
            dirTotal += 1 
        for filename in filenames:
            print os.path.join(dirname, filename)
            if tarfile.is_tarfile( filename ):
                tarball = tarfile.open(filename) 
                tarball.extractall( location ) 
                fileCount += 1 
            else:
                print "[error] "+filename
                fileIgnored += 1 
            fileTotal += 1 
    print '[DIRECTORIES]>> Total: '+str(dirTotal)+' processed: '+str(dirCount)+ ' ignored: '+str(dirIgnored) 
    print '[FILES]>> Total: '+str(fileTotal)+' processed: '+str(fileCount)+' ignored: '+str(fileIgnored) 

def extractTar( name ):
    tarball = tarfile.open( name )
    tarball.extractall( './' )

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
        main()
