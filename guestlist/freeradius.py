'''
FreeRadius functions for guestlist
'''
import radiusd

def instantiate(args):
    return radiusd.RLM_MODULE_OK

def authorize(args):
    return radiusd.RLM_MODULE_OK

def authenticate(args):
    return radiusd.RLM_MODULE_OK

def post_auth(args):
    return radiusd.RLM_MODULE_OK

def detach(args):
    return radiusd.RLM_MODULE_OK