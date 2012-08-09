from functools import wraps
from time import time

def timed(fn):
    """
    a timing decorator to log timing results
        @timed
        def somefunction(countto):
            for i in xrange(countto):
                pass
    """
    def wrapper(*args, **kwargs):
        print("calling %s(%s,%s)"%(fn.__name__,args, kwargs))
        start = time() 
        result = fn(*args, **kwargs)
        total = time() - start
        print("%s --> %s"%(fn.func_name,result))
        time_msg = "%s took %d time to finish" % (fn.__name__, total)
        logger.info(time_msg)
        return result 
    wrapper.func_name = fn.func_name
    return wrapper 
#somefunction(1000000000)
#somefunction(100000)

