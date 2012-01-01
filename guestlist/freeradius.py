'''
FreeRadius functions for guestlist
'''
# From rlm_python.c:
#
# The function returns either:
# 1. (returnvalue, replyTuple, configTuple), where
#   - returnvalue is one of the constants RLM_*
#   - replyTuple and configTuple are tuples of string
#      tuples of size 2
#
#  2. the function return value alone
#
#  3. None - default return value is set

import radiusd

import guestlist

dbfile = "/var/lib/radiusd/guestlist.db"

def _ret_tuple(value, reply, config):
    '''Build a valid radiusd response'''
    if reply is not None:
        reply = tuple(reply)
    if config is not None:
        config = tuple(config)
    return (value, reply, config)

def instantiate(args):
    '''func_instantiate for radiusd rlm_python'''
    return radiusd.RLM_MODULE_OK

def authorize(args):
    '''func_authorize for radiusd rlm_python'''
    config = [('Auth-Type', 'guestlist')]
    return _ret_tuple(radiusd.RLM_MODULE_UPDATED, None, config)


def authenticate(args):
    '''func_authenticate for radiusd rlm_python'''
    for t in args:
        if t[0] == 'User-Name':
            mac = t[1]
    if mac[0] == '"' and mac[-1] == '"':
        mac = mac[1:-1]
    gl = guestlist.GuestList(dbfile)
    if gl.authenticate(mac):
        return radiusd.RLM_MODULE_OK
    else:
        return radiusd.RLM_MODULE_NOTFOUND

def post_auth(args):
    '''func_post_auth for radiusd rlm_python'''
    return radiusd.RLM_MODULE_OK

def detach(args):
    '''func_detach for radiusd rlm_python'''
    return radiusd.RLM_MODULE_OK