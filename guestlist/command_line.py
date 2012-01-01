'''
Command Line version for GuestList management
'''

import sys
#import types

import guestlist


def show_help():
    pass

if __name__ == '__main__':
    gl = guestlist.GuestList(guestlist.DBFILE)
    #methods = [x for x in dir(gl) if not x.startswith('_') and
    #           type(getattr(gl,x)) == types.MethodType]
    method = getattr(gl, sys.argv[1])
    args = tuple(sys.argv[2:])
    if len(sys.argv) > 2:
        ret = method(*args)
    else:
        ret = method()
    
    if ret is not None:
        print ret