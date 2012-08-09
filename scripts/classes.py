import os, sys, re

class Media( object ):
    def __init__(self, *args, **kwargs):
        if not kwargs.get('map'):
            sys.exit('No mapping definition') 
        self.setup(kwargs.get('map'))
    def setup(self, mapping):
        print "setting up mapping"
        self.places = mapping['places']
        try:    
            items = [] 
            for p in self.places:
                items = items + [os.path.join(p,i) for i in os.listdir(p) for p in self.places]
        except OSError:
            print "error listing"
        self.defs = mapping['defs']    
    def get_finder( self ):
        def fn():
            places = self.places
            items = [os.listdir(p) for p in places]
            return items 
        return fn 
    def get_matcher(self, regex):
        def matcher(item):
            return regex.match(item)
        return matcher

if __name__ == "__main__":
    media_map = {
        "__default" : "download",
        "download": {
            "places" : [
                '/media/downloads', 
            ],
        },
        "video": {
            "places" : [
                '/media/hdmovies1', 
                '/media/hdmovies2', 
                '/media/hdmovies3',  
                '/media/hdmovies4', 
                '/media/movies1'
            ],
            "defs" : [
                re.compile( "([^\/]*)(\d{4})([^\/]*)" ), 
                re.compile("([^\/]*)(\d{4})([^\/]*)"), 
                re.compile("([^\/]*)[Ss](\d{2})[\.\-]([^\/]*)")
            ],
        },
        "television": {
            "places" : [
                '/media/hdtv1', 
                '/media/hdtv2', 
                '/media/tv1', 
                '/media/tv2,'
            ],
            "defs" : [
                re.compile("(\w+)\.[.m4v|.rm|.m3u|.mov|.divx|.xvid|.bivx|.vob|.img|.iso|.wmv|.avi|.mpg|.mpeg|.mp4|.mkv|.avc|.nuv|.viv|.dv|.fli|.flv]"),
                re.compile("\[[Ss]([0-9]+)\]_\[[Ee]([0-9]+)([^\\/]*)"),
                re.compile("[\._ \-]([0-9]+)x([0-9]+)([^\\/]*)"), 
                re.compile("[\._ \-][Ss]([0-9]+)[\.\-]?[Ee]([0-9]+)([^\\/]*)"),
                re.compile("[\._ \-]([0-9]+)([0-9][0-9])([\._ \-][^\\/]*)"),
                re.compile("[\._ \-]p(?:ar)?t[._ -]()([ivxlcdm]+)([\._ \-][^\\/]*)"),
            ],
        },
        "music": {
            "places" : [
                '/media/music', 
            ],
            "defs" : [
                re.compile("(\w+)\.[.m4a|.flac|.aac|.strm|.rm|.mpa|.wav|.wma|.ogg|.mp3|.mp2|.m3u]"),
            ],
        },
    }
    
    x = Media("media", map=media_map['video'])
    finder = x.get_finder()         #get a finder based on constructed class
    items = finder() 
