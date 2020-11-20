import sys
from socket import *
import http.client
import os


class SocketServer(object):
    def __init__(self, host='localhost', port=8000, back_log=10):
        print("Access http://{host}:{port}".format(host=host, port=port))
        self.socket_server = socket(AF_INET, SOCK_STREAM)
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
                self.rfile = self.client_socket.makefile('rb', -1)
                self.raw_requestline = self.rfile.readline(65537)
                self.handle_one_request()
        except KeyboardInterrupt:
            print("\nShutting down...\n")
        self.socket_server.close()

    def handle_one_request(self):
        pass


class BaseHTTPRequestHandler(SocketServer):
    def __init__(self, host='localhost', port=8000, back_log=10):
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
        self.command, self.path, self.version = command, path, version
        self.headers = http.client.parse_headers(self.rfile, _class=http.client.HTTPMessage)
        # header的一些处理后续再说
        # expect = self.headers.get('Expect', "")

    def handle_one_request(self):
        self.parse_request()
        mname = 'do_' + self.command
        if hasattr(self, mname):
            method = getattr(self, mname)
            method()

        data = "HTTP/1.1 200 OK\r\n"
        data += "Content-Type: text/html; charset=utf-8\r\n"
        data += "\r\n"
        data += "<html><body>Hello World</body></html>\r\n\r\n"
        self.client_socket.sendall(data.encode())
        self.client_socket.shutdown(SHUT_WR)

    def do_GET(self):
        pass


def main():
    s = BaseHTTPRequestHandler()
    s.listen()


if __name__ == '__main__':
    main()

'''
rbufsize = -1
self.rfile = self.client_socket.makefile('rb',rbufsize)

'''
