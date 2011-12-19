'''
GuestList class definition.
'''

class GuestList(object):
    '''
    List of MACs authorized.
    ''' 

    def __init__(self, filename):
        '''
        Create a GuestList object with filename as database.
        '''
        pass
    
    def initialize_db(self):
        '''
        Initialize an empty database.
        '''
        pass

    def authorize(self, mac, description=None):
        '''
        Add a MAC as authorized to the database.
        '''
        pass
    
    def delete(self, mac):
        '''
        Delete a MAC from the database.
        '''
        pass
    
    def authenticate(self, mac):
        '''
        Return True if a MAC is authorized.
        '''
        pass
    
    def get_info(self, mac=None):
        '''
        Return stored info about a MAC.
        
        If mac is None, return info about all MACs stored. 
        '''
        pass