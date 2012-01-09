'''GuestList database manager - HTTP server'''

import BaseHTTPServer
import base64
import urlparse
import sqlite3

import guestlist

AUTHFILE = "/var/lib/radiusd/httpauth.conf"
#AUTHFILE = "/tmp/httpauth.conf"

html_page = '''<html><body>
<div align="center"><a href="/">Inicio</a></div><hr>
{body}
</body></html>
'''

def html_table(db):
    schema = db.get_schema()
    data = db.get_data()
    html = ['<table border="1">', '<tr>']
    html.append('<th>{0}</th>'.format(schema[0]))
    html.append('<th>{0}</th>'.format(schema[1]))
    html.append('</tr>')
    for entry in data:
        html.append('<tr>')
        html.append('<td><a href="{0}">{0}</a></td>'.format(entry[0]))
        html.append('<td>{0}</td>'.format(entry[1]))
        html.append('</tr>')
    return '\n'.join(html)

def html_mac(db, mac):
    data = db.get_data(mac)
    data = data.pop() #TODO: check data is not empty
    html = '''<strong>{0}</strong><br><em>{1}</em>
    <form action="/delete" method="post">
    <input type="hidden" name="mac" value="{0}">
    <input type="submit" value="Delete">
    </form>'''.format(data[0], data[1])
    return html

html_authorize_form = '''
<div><form action="/authorize" method="post">
Mac: <input type="text" name="mac" size=20><br>
Description: <input type="text" name="description"><br>
<input type="submit" value="Authorize">
</form></div>
'''

def html_post_authorize(db, form):
    try:
        description = form['description']
    except KeyError:
        description = None
    try:
        mac = form['mac']
    except KeyError:
        return '''<strong>Missing MAC address!</strong>'''
    try:
        db.authorize(mac, description)
    except ValueError:
        return '''<strong>Invalid MAC address!</strong>'''
    except sqlite3.IntegrityError:
        return '''<strong>MAC previously authorized!</strong>'''
    except sqlite3.Error:
        return '''<strong>Database Error!</strong>'''
    
    return '''<p>MAC <em>{0}</em> authorized</p>'''.format(mac) 

def html_post_delete(db, form):
    try:
        mac = form['mac']
    except KeyError:
        return '''<strong>Invalid POST request!</strong>'''
    try:
        db.delete(mac)
    except ValueError:
        return '''<strong>Invalid MAC address!</strong>'''
    return '''<p>MAC <em>{0}</em> deleted from database'''.format(mac)

class ReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    auth = None
    server_version = 'guestlist/0.1'
    
    def validate_auth(self):
        if self.auth is None:
            with open(AUTHFILE) as f:
                self.auth = f.read()
            self.auth = base64.b64encode(self.auth)
            self.auth = 'Basic ' + self.auth
        auth = self.headers.get('Authorization')
        return auth == self.auth

    def send_auth_request(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate',
                         'Basic realm="%s"' % self.server_version)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write('Valid username and password requeried')

    def send_html(self, body):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html_page.format(body=body))

    def form_decode(self):
        length = int(self.headers.get('Content-Length', '0'))
        d = urlparse.parse_qs(self.rfile.read(length))
        for k in d.keys():
            d[k] = d[k][0]
        return d

    def do_GET(self):
        if not self.validate_auth():
            self.send_auth_request()
            return
        
        db = guestlist.GuestList(guestlist.DBFILE)
        
        if self.path == '/':
            self.send_html(html_authorize_form + '<hr>' + html_table(db))
            return
        try:
            html = html_mac(db, self.path.lstrip('/'))
        except ValueError:
            self.send_error(404)
            return
        self.send_html(html)

    def do_POST(self):
        if not self.validate_auth():
            self.send_auth_request()
            return
        
        form = self.form_decode()
        
        #print ' '.join(['POST ',self.path, self.request_version])
        #print self.headers
        #print form
        
        db = guestlist.GuestList(guestlist.DBFILE)
        if self.path == '/authorize':
            self.send_html(html_post_authorize(db, form))
            return
        
        if self.path == '/delete':
            self.send_html(html_post_delete(db,form))
            return
        
        self.send_error(404)

if __name__ == '__main__':
    addr = ('', 8080)
    httpd = BaseHTTPServer.HTTPServer(addr, ReqHandler)
    httpd.serve_forever()
