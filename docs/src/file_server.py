from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import sys

# [error_page]
ERROR_PAGE = """\
<html>
  <head><title>Error accessing {path}</title></head>
  <body>
    <h1>Error accessing {path}: {msg}</h1>
  </body>
</html>
"""
# [/error_page]

# [exception]
class ServerException(Exception):
    pass
# [/exception]

# [do_get]
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url_path = self.path.lstrip("/")
            full_path = Path.cwd().joinpath(url_path)
            print(f"'{self.path}' => '{full_path}'")
            if not full_path.exists():
                raise ServerException(f"{self.path} not found")
            elif not full_path.is_file():
                raise ServerException(f"{self.path} not file")
            else:
                self.handle_file(self.path, full_path)
        except Exception as msg:
            self.handle_error(msg)
# [/do_get]

    # [handle_file]
    def handle_file(self, given_path, full_path):
        try:
            with open(full_path, "rb") as reader:
                content = reader.read()
            self.send_content(content, HTTPStatus.OK)
        except IOError:
            raise ServerException(f"Cannot read {given_path}")
    # [/handle_file]

    # [handle_error]
    def handle_error(self, msg):
        content = ERROR_PAGE.format(path=self.path, msg=msg)
        content = bytes(content, "utf-8")
        self.send_content(content, HTTPStatus.NOT_FOUND)
    # [/handle_error]

    # [send_content]
    def send_content(self, content, status):
        self.send_response(int(status))
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    # [/send_content]

# [main]
if __name__ == "__main__":
    os.chdir(sys.argv[1])
    serverAddress = ("", 8000)
    server = HTTPServer(serverAddress, RequestHandler)
    print(f"serving in {os.getcwd()}...")
    server.serve_forever()
# [/main]
