import socket
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

from mcp_spotify_player.client_auth import ALL_COMMANDS, build_success_page


def test_callback_serves_html():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = build_success_page()
            self.wfile.write(html.encode("utf-8"))

        def log_message(self, *args, **kwargs):
            return

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    httpd = HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()

    res = urllib.request.urlopen(f"http://127.0.0.1:{port}/")
    html = res.read().decode()

    httpd.shutdown()
    thread.join()

    assert res.status == 200
    assert res.headers["Content-Type"] == "text/html; charset=utf-8"
    assert "mcp-spotify-player" in html
    assert "https://github.com/vsaez/mcp-spotify-player" in html
    assert all(cmd in html for cmd in ALL_COMMANDS)
