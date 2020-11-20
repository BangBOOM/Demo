import atexit
import os
import posixpath
from socket import *
import sys
import signal

config = None
back_log = 10
host = 'localhost'


class SocketServer(object):
    def __init__(self, ):

        self.socket_server = socket(AF_INET, SOCK_STREAM)
        while True:
            try:
                self.socket_server.bind(('localhost', config['port']))
                self.socket_server.listen(back_log)
                break
            except Exception:
                pass
            # self.socket_server.close()
            # exit()
            # for proc in process_iter():
            #     for conns in proc.connections(kind='inet'):
            #         if conns.laddr.port == config['port']:
            #             proc.send_signal(SIGKILL)  # or SIGKILL
            # self.socket_server.bind(('localhost', config['port']))
            # self.socket_server.listen(back_log)
        # print("Access http://{host}:{port}".format(host=host, port=config['port']))

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
        except:
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
    protocol_version = "HTTP/1.1"

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
        print(self.path)
        if self.path[1:] in os.listdir(config['staticfiles']) or self.path == '/':
            if self.path == '/':
                path = config['staticfiles'] + "/index.html"
                c_type = self.guess_type(path)
            else:
                path = config['staticfiles'] + self.path
                c_type = self.guess_type(self.path)
            self.send_response(*self.OK)
            self.send_header("Content-type", c_type)
            self.end_header()
            return path

        return None

    def do_GET(self):
        path = self.send_head()
        if path:
            with open(path, 'rb') as f:
                r = f.read()
                print(r.decode())
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
        ws = BaseWebServer()
        ws.listen()
        atexit.register(handle_exit, ws.socket_server)
        signal.signal(signal.SIGTERM, handle_exit)
        signal.signal(signal.SIGINT, handle_exit)
