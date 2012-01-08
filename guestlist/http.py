'''GuestList database manager - HTTP server'''

import BaseHTTPServer
import base64

import guestlist

AUTHFILE = "/var/lib/radius/httpauth.conf"
#AUTHFILE = "/tmp/httpauth.conf"

html_page = '''<html><body>
<a href="/">Inicio</a><br>
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
    data = data.pop()
    html = '''MAC: {0}<br> Desc: {1}'''.format(data[0], data[1])
    return html

html_authorize = '''
<form>
Mac: <input type="text" name="mac" /><br />
Description: <input type="text" name="description" /><br />
<input type="submit" value="Submit" />
</form>
'''

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

    def do_GET(self):
        if not self.validate_auth():
            self.send_auth_request()
            return
        
        db = guestlist.GuestList(guestlist.DBFILE)
        
        if self.path == '/':
            self.send_html(html_table(db))
            return
        try:
            html = html_mac(db, self.path.lstrip('/'))
        except ValueError:
            self.send_error(404)
            return
        self.send_html(html)
   
if __name__ == '__main__':
    addr = ('', 8080)
    httpd = BaseHTTPServer.HTTPServer(addr, ReqHandler)
    httpd.serve_forever()
