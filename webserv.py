import posixpath
import sys
import urllib
from socket import *
import http.client
import os
import http.server


class SocketServer(object):
    def __init__(self, host='localhost', port=8070, back_log=10):
        print("Access http://{host}:{port}".format(host=host, port=port))
        self.socket_server = socket(AF_INET, SOCK_STREAM)
        self.response = b""
        try:
            self.socket_server.bind((host, port))
            self.socket_server.listen(back_log)
        except Exception as exc:
            print("Error:")
            print(exc)

    def listen(self):
        try:
            while True:
                self.client_socket, self.address = self.socket_server.accept()
                '''print address'''
                print("%s:%d" % self.address, end=' ')

                self.rfile = self.client_socket.makefile('rb', -1)
                self.raw_requestline = self.rfile.readline(65537)
                self.handle_one_request()
        except KeyboardInterrupt:
            print("\nShutting down...\n")
        self.socket_server.close()

    def handle_one_request(self):
        pass


class BaseHTTPRequestHandler(SocketServer):
    OK = 200, 'OK'
    protocol_version = "HTTP/1.1"

    def __init__(self, staticfiles, cgibin, exec, port=8000, back_log=10, host='localhost'):
        if not isinstance(port, int):
            port = int(port)
        super(BaseHTTPRequestHandler, self).__init__(host=host, port=port, back_log=back_log)

    def parse_request(self):
        self.command = None
        self.request_version = "HTTP/0.9"

        requestline = str(self.raw_requestline, 'iso-8859-1').rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        command, path, version = [None] * 3
        if len(words) == 3:
            command, path, version = words
        print(' '.join(words))
        self.command, self.path, self.version = command, path, version
        self.headers = http.client.parse_headers(self.rfile, _class=http.client.HTTPMessage)
        # header的一些处理后续再说
        # expect = self.headers.get('Expect', "")
        # print(self.headers.get('Accept'))

    def handle_one_request(self):
        self.parse_request()
        mname = 'do_' + self.command
        if hasattr(self, mname):
            method = getattr(self, mname)
            method()

        self.client_socket.sendall(self.response)
        self.client_socket.shutdown(SHUT_WR)
        self.response = b""

    def do_GET(self):
        path = self.send_head()

        if os.path.isfile(path):
            with open(path, 'rb') as f:
                r = f.read()
            self.response += r

    def guess_type(self, path):
        extensions_map = {
            '': 'application/ostet-stream',
            '.py': 'text/plain',
            '.txt': 'text/plain',
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.xml': 'text:xml',
            '.html': 'text:html',
        }

        base, ext = posixpath.splitext(path)
        if ext in extensions_map:
            return extensions_map[ext]
        else:
            return extensions_map['']

    def send_response(self, code, message=None):
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(("%s %d %s\r\n" %
                                     (self.protocol_version, code, message)).encode(
            'latin-1', 'strict'))

    def send_header(self, keyword, value):
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(
            ("%s: %s\r\n" % (keyword, value)).encode('latin-1', 'strict')
        )

    def end_header(self):
        self._headers_buffer.append(b"\r\n")
        self.response += b"".join(self._headers_buffer)
        self._headers_buffer = []

    def send_head(self):
        path = self.translate_path(self.path)
        ctype = self.guess_type(path)
        self.send_response(*self.OK)
        self.send_header("Content-type", ctype)
        self.end_header()

        self._headers_buffer.append(b"\r\n")
        return path

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = filter(None, words)

        path = os.getcwd() + "\\files"

        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path


def main(config):
    s = BaseHTTPRequestHandler(**config)
    s.listen()


if __name__ == '__main__':
    c = dict()
    try:
        config = sys.argv[1]
        with open(config, 'r', encoding='utf-8') as f:
            c = {
                l.split('=')[0]: l.split('=')[1]
                for l in f.read().split('\n') if '=' in l
            }
    except Exception as exc:
        print("Unable To Load Configuration File")
    main(c)

'''
rbufsize = -1
self.rfile = self.client_socket.makefile('rb',rbufsize)
'''
