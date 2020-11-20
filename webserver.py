"""
author:Wenquan Yang
time:2020/11/20 22:07
"""
from socket import *
import sys


class SocketServer(object):
    def __init__(self, host='localhost', port=8070, back_log=10):

        self.socket_server = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket_server.bind((host, port))
            self.socket_server.listen(back_log)
        except Exception as exc:
            print("Error:", exc)
        print("Access http://{host}:{port}".format(host=host, port=port))

    client_info = []
    response = b""
    raw_request_line = b""

    def listen(self):
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

    def handle_one_request(self):
        pass

    def clear(self):
        self.client_info = []
        self.response = b""
        self.raw_request_line = b""


class BaseWebServer(SocketServer):
    def __init__(self, host='localhost', port=8070, back_log=10):
        super(BaseWebServer, self).__init__(host=host, port=port, back_log=back_log)

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
        print(" ".join(self.client_info))

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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Missing Configuration Argument", end='')
    else:
        config_path = sys.argv[1]
        with open(config_path, 'r', encoding='utf-8') as f:
            config = {
                l.split('=')[0]: l.split('=')[1]
                for l in f.read().split('\n') if '=' in l
            }
            for key in ('staticfiles', 'cgibin', 'port', 'exec'):
                if key not in config:
                    print("Missing Field From Configuration File", end='')
        # ws = BaseWebServer()
        # ws.listen()
