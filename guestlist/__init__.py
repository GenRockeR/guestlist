'''
GuestList class definition.
'''
import os
import sqlite3
import logging

VERSION = 1
DBFILE = "/var/lib/radiusd/guestlist.db"

class GuestList(object):
    '''
    List of authorized MACs.
    '''

    def _get_version(self):
        '''Return database version or 0 if not valid'''
        version = 0
        try:
            row = self.db.execute("SELECT version FROM dbinfo;").fetchone()
            if row is not None:
                version = row[0]
        except sqlite3.OperationalError:
            pass
        return version
    
    def _mac_cleanup(self, mac):
        digits = set('0123456789abcdef')
        macarg = mac
        mac = mac.translate(None,'.:- ').lower()
        if not digits.issuperset(set(mac)) or not len(mac) == 12:
            raise ValueError('Invalid MAC address format ' + macarg)
        return mac

    def __init__(self, filename):
        '''
        Create a GuestList object with filename as database.
        '''
        self.log = logging.getLogger(__name__)
        self.filename = os.path.abspath(filename)
        self.log.info("Connecting to database: %s", self.filename)
        self.db = sqlite3.connect(self.filename)
        version = self._get_version()

        if version == 0:
            self.initialize_db()
        else:
            self.version = version

        if self.version > VERSION:
            msg = "Database schema version %d, not supported" % self.version
            self.log.critical(msg)
            raise NotImplementedError(msg)
        elif self.version < VERSION:
            self.log.warning("Database schema version %s, out of date. "
                             "Upgrade the schema to version %s for modifying "
                             "data.", self.version, VERSION)

    def __del__(self):
        self.db.close()

    def initialize_db(self):
        '''
        Initialize an empty database.
        '''
        self.log.info("Initializing database version %s", VERSION)
        self.db.executescript("""
            DROP TABLE IF EXISTS dbinfo;
            DROP TABLE IF EXISTS guestlist;
            CREATE TABLE dbinfo (version, check (rowid == 1));
            CREATE TABLE guestlist (mac UNIQUE NOT NULL, description);
            INSERT INTO dbinfo VALUES(1);
        """)
        self.db.commit()
        self.version = VERSION

    def authorize(self, mac, description=None):
        '''
        Add a MAC as authorized to the database.
        '''
        mac = self._mac_cleanup(mac)
        t = (mac, description)
        if self.version == VERSION:
            self.db.execute("INSERT INTO guestlist VALUES (?,?);", t)
            self.db.commit()
            self.log.info("MAC %s authorized", mac)
        else:
            self.log.error("Old version databases can not change data. "
                           "Please, upgrade to version %s", VERSION)

    def delete(self, mac):
        '''
        Delete a MAC from the database.
        '''
        mac = self._mac_cleanup(mac)
        t = (mac, )
        if self.version == VERSION:
            self.db.execute("DELETE FROM guestlist WHERE mac=?;", t)
            self.db.commit()
            self.log.info("MAC %s deleted", mac)
        else:
            self.log.error("Old version databases can not change data. "
                           "Please, upgrade to version %s", VERSION)

    def authenticate(self, mac):
        '''
        Return True if a MAC is authorized.
        '''
        mac = self._mac_cleanup(mac)
        t = (mac, )
        auth = False
        if self.version == 1:
            row = self.db.execute("SELECT mac FROM guestlist WHERE mac=?;",
                                  t).fetchone()
            auth = row is not None
        return auth
    
    def get_schema(self):
        '''
        Return a tuple of column headers.
        '''
        q = self.db.execute("SELECT * from guestlist")
        hdrs = tuple([x[0] for x in q.description])
        return hdrs

    def get_data(self, mac=None):
        '''
        Return stored info about a MAC.
        
        If mac is None, return info about all stored MACs. 
        '''
        if mac is None:
            q = self.db.execute("SELECT * from guestlist;")
        else:
            mac = self._mac_cleanup(mac)
            t = (mac, )
            q = self.db.execute("SELECT * from guestlist WHERE mac=?", t)
        return q.fetchall()

