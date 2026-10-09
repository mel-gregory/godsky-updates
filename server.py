#!/usr/bin/env python3
"""Minimal static file server for the God Sky Network updates blog."""
import http.server
import os

PORT = int(os.environ.get("PORT", "8080"))

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass  # quiet

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    httpd.serve_forever()
