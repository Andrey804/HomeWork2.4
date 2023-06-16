import socket
import mimetypes
import pathlib
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote_plus
from datetime import datetime
from threading import Thread


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        pr_url = urlparse(self.path)

        if pr_url.path == '/':
            self.render_template('index.html')
        elif pr_url.path == '/message.html':
            self.render_template('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.render_template('error.html', 404)

    def do_POST(self):

        data = self.rfile.read(int(self.headers['Content-Length']))

        simple_client(HOST, PORT_S, data)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_static(self):

        self.send_response(200)
        mt = mimetypes.guess_type(self.path)

        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def render_template(self, filename, status=200):

        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


def echo_server(host, port):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv = host, port
    sock.bind(serv)

    try:
        while True:
            data, address = sock.recvfrom(1024)
            data_parse = unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}

            with open("storage/data.json", "r") as fh:
                jsonfile = json.load(fh)
                jsonfile.update({str(datetime.now()): data_dict})

            with open("storage/data.json", "w") as fh:
                json.dump(jsonfile, fh)

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


def simple_client(host, port, message):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv = host, port

    sock.sendto(message, serv)
    sock.close()


if __name__ == "__main__":

    HOST = 'localhost'
    PORT_H = 3000
    PORT_S = 5000

    server = HTTPServer((HOST, PORT_H), HttpHandler)
    server_thread = Thread(target=server.serve_forever)

    server_socket = Thread(target=echo_server, args=(HOST, PORT_S))

    server_thread.start()
    server_socket.start()
