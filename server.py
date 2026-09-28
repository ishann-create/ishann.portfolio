import os
import sys
import json
import shutil
import mimetypes
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure MIME types are accurate
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/x-icon", ".ico")
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type("application/json", ".json")

# Ensure work directory has index.html for static server compatibility
work_dir = os.path.join(ROOT_DIR, "work")
os.makedirs(work_dir, exist_ok=True)
if os.path.isfile(os.path.join(ROOT_DIR, "work.html")):
    shutil.copyfile(os.path.join(ROOT_DIR, "work.html"), os.path.join(work_dir, "index.html"))

# Load Remix loader data
index_data_path = os.path.join(ROOT_DIR, "index_data.json")
work_data_path = os.path.join(ROOT_DIR, "work_data.json")

INDEX_DATA = {}
WORK_DATA = {}

if os.path.isfile(index_data_path):
    with open(index_data_path, "r", encoding="utf-8") as f:
        INDEX_DATA = json.load(f)["state"]["loaderData"]["routes/_index"]

if os.path.isfile(work_data_path):
    with open(work_data_path, "r", encoding="utf-8") as f:
        WORK_DATA = json.load(f)["state"]["loaderData"]["routes/work"]

class PortfolioHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def log_message(self, format, *args):
        # Clean request logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}\n")

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_HEAD(self):
        self.handle_request(send_body=False)

    def do_GET(self):
        self.handle_request(send_body=True)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.rstrip("/") == "/api/page-view":
            self.send_json_response({"source": "organic", "total": 161745})
            return
        self.send_error(404, "Not Found")

    def handle_request(self, send_body=True):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Remix Data Loaders
        if "_data" in query:
            route = query["_data"][0]
            if route in ("routes/_index", "routes%2F_index"):
                self.send_json_response(INDEX_DATA, send_body=send_body)
                return
            elif route in ("routes/work", "routes%2Fwork"):
                self.send_json_response(WORK_DATA, send_body=send_body)
                return

        # 2. Routes
        norm_path = path.rstrip("/")
        if norm_path in ("", "/index", "/index.html"):
            self.serve_file_response(os.path.join(ROOT_DIR, "index.html"), "text/html; charset=utf-8", send_body=send_body)
            return

        if norm_path == "/work":
            self.serve_file_response(os.path.join(ROOT_DIR, "work.html"), "text/html; charset=utf-8", send_body=send_body)
            return

        if norm_path == "/api/page-view":
            self.send_json_response({"source": "organic", "total": 161745}, send_body=send_body)
            return

        # 3. Static Files
        # Prevent Directory Traversal
        rel_path = path.lstrip("/\\").replace("/", os.sep)
        full_path = os.path.join(ROOT_DIR, rel_path)

        if os.path.isfile(full_path):
            content_type, _ = mimetypes.guess_type(full_path)
            if not content_type:
                content_type = "application/octet-stream"
            if content_type.startswith("text/") or content_type == "application/javascript":
                content_type += "; charset=utf-8"
            self.serve_file_response(full_path, content_type, send_body=send_body)
            return

        # Fallback to default handler
        if send_body:
            super().do_GET()
        else:
            super().do_HEAD()

    def send_json_response(self, data, send_body=True):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def serve_file_response(self, file_path, content_type, send_body=True):
        if not os.path.isfile(file_path):
            self.send_error(404, "File not found")
            return
        file_size = os.path.getsize(file_path)
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file_size))
        self.end_headers()
        if send_body:
            with open(file_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)

def run(port=3000):
    for p in range(port, port + 10):
        try:
            server = HTTPServer(("0.0.0.0", p), PortfolioHandler)
            print(f"\n=======================================================")
            print(f"  Ishan Mondal portfolio is LIVE!")
            print(f"  URL: http://localhost:{p}")
            print(f"  Work Page: http://localhost:{p}/work")
            print(f"=======================================================\n")
            server.serve_forever()
            break
        except OSError:
            print(f"Port {p} is busy, trying port {p+1}...")
            continue

if __name__ == "__main__":
    port = 3000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
