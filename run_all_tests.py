from test import tfile, theaders, tparser
from las.util import each

def run_tests(suite):
    for test in suite.tests:
        test()

def do_tests():
    print "suite file"
    run_tests(tfile)
    print "------------"
    print "suite headers"
    run_tests(theaders)
    print "------------"
    print "suite tparser"
    run_tests(tparser)
    print "------------"

if __name__ == "__main__":
    do_tests()
