'''
Created on 04/01/2012

@author: rmorales
'''
import BaseHTTPServer
import base64

import guestlist

AUTHFILE = "/var/lib/radius/httpauth.conf"
#AUTHFILE = "/tmp/httpauth.conf"

class ReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    auth = None
    
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
        self.wfile.write('Username and password requeried')

    def send_index(self):
        gl = guestlist.GuestList(guestlist.DBFILE)
        schema = gl.get_schema()
        data = gl.get_data()
        html = ['<html><body>', '<table border="1">', '<tr>']
        html.append('<th>{0}</th>'.format(schema[0]))
        html.append('<th>{0}</th>'.format(schema[1]))
        html.append('</tr>')
        for entry in data:
            html.append('<tr>')
            html.append('<td><a href="{0}">{0}</a></td>'.format(entry[0]))
            html.append('<td>{0}</td>'.format(entry[1]))
            html.append('</tr>')
        html.append('</body></html>')
        body = '\n'.join(html)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(body)

    def send_authorize(self):
        html = '''<html><body>
<form>
Mac: <input type="text" name="mac" /><br />
Description: <input type="text" name="description" /><br />
<input type="submit" value="Submit" />
</form>
</body></html>'''
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html)

    def do_GET(self):
        if not self.validate_auth():
            self.send_auth_request()
            return
        
        if self.path == '/':
            self.send_index()
            return
        
        if self.path == '/authorize':
            self.send_authorize()
            return
        
        self.send_error(404)
   
if __name__ == '__main__':
    addr = ('', 8080)
    httpd = BaseHTTPServer.HTTPServer(addr, ReqHandler)
    httpd.serve_forever()
