from time import time
def only_if(condition):
    def g(method):
        mname = method.__name__
        if condition:
            def f(*args, **kwargs):
                return method(*args, **kwargs)
            f.__name__ = mname
            return f
        else:
            def f(*args, **kwargs):
                print "skipping %s " % mname
            f.__name__ = mname
            return f
    return g
            
def test(tests, method):
    mname = method.__name__
    def f():
        start = time()
        method()
        end = time()
        print "finished %s in %s" % (mname, end - start)
    f.__name__ = mname
        
    tests.append(f)
    return f    

