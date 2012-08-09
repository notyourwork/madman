"""
media source
    /media/downloads/ircdownloads/complete/
    /media/downloads/seeding/
media destiations 
    video   ^[\w+]\.[mkv|avi]$
        hd video
            /media/hdmovies1/ 
                ^[0-9A-F]
            /media/hdmovies2/ 
                ^[G-J]
            /media/hdmovies3/ 
                ^[K-P]
            /media/hdmovies4/ 
                ^[Q-Z]
        sd video
            /media/movies1/   
                ^[0-9A-G]
            /media/movies2/   
                ^[H-Z]
        hd tv
            /media/hdtv1/
            /media/hdtv2/
        sd tv  
            /media/tv1/
            /media/tv2/
    audio 
        /media/music/
            a
            b
            c
            ...
            x
            y
            z
    image 
       
    application
        game 
            /media/isos1/Games/
        application 
            /media/isos1/Applications/

media operations 
    process -> fn, options, command 
    move -> fn
    cron  -> fn 
        
command has options and options get parameters 
    

You have media destinations and media sources 
Need dynamically defined command options 
    based on operations defined 
"""
     
function_map = {
    'process':process, 
    'is_type':is_type,
    'list':list_media, 
}

location_map = {
    "__default" : "download",
    "download": {
        "places" : [
            '/media/donwloads', 
        ],
        "definitions" : [
            re.compile(
        ]
    },
    "video": {
        "places" : [
            '/media/hdmovies1', 
            '/media/hdmovies2', 
            '/media/hdmovies3',  
            '/media/hdmoves4', 
            '/media/movies1'
        ],
        "definitions" : [
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
        ],
        "definitions" : [
            re.compile("(\w+)\.[mp3|m4a|aac|wav]"),
        ],
    },
    "music": {
        "places" : [
            '/media/music', 
        ],
        "definitions" : [
            re.compile("(\w+)\.[mp3|m4a|aac|wav]"),
        ],
    },
    "image": {
        "places" : [
            '/media/images', 
        ],
        "definitions" : [
            re.compile("(\w+)\.[jpg|jpeg|png|gif]"),
        ]
    },
}
