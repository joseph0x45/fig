import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/files':
            files = sorted(f for f in os.listdir('.') if f.endswith('.json'))
            body = json.dumps(files).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    server = HTTPServer(('', 8000), Handler)
    print('Serving at http://localhost:8000')
    server.serve_forever()
