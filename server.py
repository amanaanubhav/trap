import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8501))


# always return index.html no matter what path is hit
class FallbackHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    print(f"serving fallback on :{PORT}")
    server = HTTPServer(("0.0.0.0", PORT), FallbackHandler)
    server.serve_forever()
