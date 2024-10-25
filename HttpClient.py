from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    httpRequestHandler=None
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'message': 'This is a GET request'}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        self.httpRequestHandler(data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'message': 'This is a POST request', 'data': data}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def runServer(port,httpRequestHandler):
    print(f'[HTTPSERVER] Starting httpd server on port {port}...')
    server_class=HTTPServer
    handler_class=SimpleHTTPRequestHandler
    handler_class.httpRequestHandler = httpRequestHandler
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()