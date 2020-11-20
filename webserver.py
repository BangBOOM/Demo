import copy
import sys
import os
import posixpath
from socket import *

__version__ = "0.1"

config = None
back_log = 10
host = '127.0.0.1'

DEFAULT_ERROR_MESSAGE = b"""<html>\n<head>\n\t<title>404 Not Found</title>\n</head>\n<body bgcolor="white">\n<center>\n\t<h1>404 Not Found</h1>\n</center>\n</body>\n</html>\n"""


class SocketServer(object):
    def __init__(self, ):
        self.socket_server = socket(AF_INET, SOCK_STREAM)
        # while True:
        try:
            # if self.allow_reuse_address:
            self.socket_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket_server.bind(('localhost', config['port']))
            self.socket_server.listen(back_log)
            print("start")

        except Exception as exc:
            # continue
            print(exc)

    client_info = []
    response = b""
    raw_request_line = b""

    def listen(self):
        try:
            while True:
                self.client_socket, self.address = self.socket_server.accept()
                self.client_info.append("{0}:{1}".format(*self.address))

                self.r_file = self.client_socket.makefile('rb', -1)
                self.raw_request_line = self.r_file.readline(65537)

                self.handle_one_request()

                # send response
                self.client_socket.sendall(self.response)
                self.client_socket.shutdown(SHUT_WR)

                # clear buffer
                self.clear()
        except Exception as exc:
            print(exc)
            self.socket_server.close()
        self.socket_server.close()

    def handle_one_request(self):
        pass

    def clear(self):
        self.client_info = []
        self.response = b""
        self.raw_request_line = b""


class BaseWebServer(SocketServer):
    OK = 200, 'OK'
    FNF = 404, 'File not found'
    protocol_version = "HTTP/1.1"

    sys_version = "Python/" + sys.version.split()[0]
    server_version = "BaseHTTP/" + __version__

    r_type = ''

    def __init__(self):
        super(BaseWebServer, self).__init__()

    def parse_request(self):
        request_line = str(self.raw_request_line, 'iso-8859-1').rstrip('\r\n')
        self.client_info.append(request_line)
        self.request_line = request_line
        words = request_line.split()
        '''
        words check to be implement, now this is not necessary
        '''
        self.command, self.path, self.version = words
        '''
        command can be GET,POST,HEAD...
        '''

        # show the request info like this
        # <host>:<port> method path version
        # '127.0.0.1:13177 GET / HTTP/1.1'
        # print(" ".join(self.client_info))

        '''
        also some header information to be implement
        self.headers = http.client.parse_headers(self.rfile, _class=http.client.HTTPMessage)
        '''

    def handle_one_request(self):
        self.parse_request()
        method_name = 'do_' + self.command
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method()
        '''
        wrong method to be handle
        '''

    def send_response(self, code, message=None):
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(("%s %d %s\n" %
                                     (self.protocol_version, code, message)).encode(
            'latin-1', 'strict'))

    def send_header(self, keyword, value):
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(
            ("%s: %s\n" % (keyword, value)).encode('latin-1', 'strict')
        )

    def end_header(self):
        self._headers_buffer.append(b"\r\n")
        self.response += b"".join(self._headers_buffer)
        self._headers_buffer = []

    def send_head(self):
        print(self.path)
        if self.path[1:] in os.listdir(config['staticfiles']) or self.path == '/':
            if self.path == '/':
                path = config['staticfiles'] + "/index.html"
                c_type = self.guess_type(path)
            else:
                path = config['staticfiles'] + self.path
                c_type = self.guess_type(self.path)
            self.send_response(*self.OK)
            self.send_header("Content-Type", c_type)
            self.end_header()
            return path
        if self.path[1:] in os.listdir(config['cgibin']):
            path = config['cgibin'] + self.path
            c_type = self.guess_type(self.path)
            return path
        return None

    def do_GET(self):
        path = self.send_head()
        if path:
            with open(path, 'rb') as f:
                r = f.read()
            self.response += r
        else:
            self.response += DEFAULT_ERROR_MESSAGE.encode()

    def do_HEAD(self):
        self.send_head()
        if self.path[1:] in os.listdir(config['staticfiles']) or self.path == '/':
            self.send_response(*self.OK)
        else:
            l = self.path.split('/')[1:]
            if len(l) == 2 and l[1] in os.listdir(config['cgibin']):
                self.send_response(*self.OK)
            else:
                self.send_response(*self.FNF)
        self.end_header()

    def guess_type(self, path):
        extensions_map = {
            '': 'application/ostet-stream',
            '.py': 'text/html',
            '.txt': 'text/plain',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.xml': 'text/xml',
            '.html': 'text/html',
        }

        base, ext = posixpath.splitext(path)
        self.r_type = ext
        if ext in extensions_map:
            return extensions_map[ext]
        else:
            return extensions_map['']

    def version_string(self):
        return self.server_version + ' ' + self.sys_version


class CGIWebServer(BaseWebServer):
    have_fork = hasattr(os, 'fork')

    def __init__(self):
        super(CGIWebServer, self).__init__()

    def run_cgi(self, path):
        env = copy.deepcopy(os.environ)
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = 'cgi.web.server'
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['SERVER_PORT'] = str(config['port'])
        env['REQUEST_METHOD'] = self.command
        # uqrest = urllib.parse.unquote(rest)
        # env['PATH_INFO'] = uqrest
        # env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        # env['SCRIPT_NAME'] = scriptname
        import subprocess
        cmd = 'python ' + path
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        p.kill()
        return out

    def send_head(self):
        print(self.path)
        if self.path[1:] in os.listdir(config['staticfiles']) or self.path == '/':
            if self.path == '/':
                path = config['staticfiles'] + "/index.html"
                c_type = self.guess_type(path)
            else:
                path = config['staticfiles'] + self.path
                c_type = self.guess_type(self.path)
            self.send_response(*self.OK)
            self.send_header("Content-Type", c_type)
            self.end_header()
            return path
        if len(self.path.split('/')) == 3:
            p1, p2 = self.path.split('/')[1:]
            if p1 == 'cgibin' and p2 in os.listdir(config['cgibin']):
                path = config['cgibin'] + '/' + p2
                c_type = self.guess_type(self.path)
                self.send_response(*self.OK)
                self.send_header("Content-type", c_type)
                self.end_header()
                return path

        c_type = self.guess_type(self.path)
        self.send_response(*self.FNF)
        self.send_header("Content-type", c_type)
        self.end_header()
        return None

    def do_HEAD(self):
        self.send_head()

    def do_GET(self):
        path = self.send_head()
        if path:
            if self.r_type == '.py':
                out = self.run_cgi(path)
                self.response += out
                return
            with open(path, 'rb') as f:
                r = f.read()
            self.response += r
        else:
            self.response += DEFAULT_ERROR_MESSAGE


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Missing Configuration Argument")
    else:
        config_path = sys.argv[1]
        with open(config_path, 'r', encoding='utf-8') as f:
            config = {
                l.split('=')[0]: l.split('=')[1]
                for l in f.read().split('\n') if '=' in l
            }
            for key in ('staticfiles', 'cgibin', 'port', 'exec'):
                if key not in config:
                    print("Missing Field From Configuration File")
                    exit()
                if key == 'port':
                    config[key] = int(config[key])
        ws = CGIWebServer()
        ws.listen()
