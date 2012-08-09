import sys, re, mimetypes
from clint.textui import colored, puts 
from optparse import OptionParser
import functions as mf
 
def get_parser():
    #define options for execution
    parser = OptionParser()
    parser.add_option(
        "-l", "--location", 
        dest="location", 
        default=mf.location_map['__default'],
        help="Location(s) to process",
        choices=[l for l in mf.location_map if l[:2] != '__'] 
    )
    parser.add_option(
        "-f", 
        "--function", 
        dest="function",
        default="process",
        help="Function to execute",
        choices=[f for f in mf.function_map]
    )
    parser.add_option(
        "-d", "--debug", 
        dest="debug", 
        action="store_true", 
        default=False, 
        help="Debugging level during execution"
    )
    parser.add_option(
        "-v", "--verbose", 
        dest="verbose", 
        action="store_true",
        help="Verbosity level"
    )
    parser.add_option(
        "-q", "--query", 
        dest="query", 
        default="",
        help="Query string, additional arguments for called function"
    )
    return parser 

def call(function, *args, **kwargs):
    '''input a string associated with a function
    and make call to this function passing it
    the additional arguments passed to this 
    function'''
    try:
        mf.function_map[function](*args, **kwargs)
    except KeyError:
        sys.exit(colored.red("`%s` is not a defined function." %( function))) 

def main():
    puts(colored.green('Running Madmanager.'))
    parser = get_parser() 
    (options, args) = parser.parse_args()
    print type(options)
    print dir(options)
    parameters = {}
    if options.verbose:
        print colored.yellow("madmanager options:%s args:%s" % (options, args))
    if options.location:
        parameters['location'] = options.location
    if options.query:
        parameters['query'] = options.query
    call(options.function,**parameters)         

if __name__ == "__main__":
    main()
    
