from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
from withdraw import subs
logging.basicConfig(level=logging.CRITICAL)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = json.dumps(list(subs))
        self.wfile.write(response.encode("utf-8"))

def start_server():
    server_address = ("", 8765)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()