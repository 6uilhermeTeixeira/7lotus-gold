"""Local Gold Lotus UI and same-origin gateway for the existing panel services."""

from __future__ import annotations

import http.client
import mimetypes
import os
import re
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
HOST = "127.0.0.1"
PORT = int(os.environ.get("LOTUS_UI_PORT", "7771"))
SOCKET_DIR = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
PANELS = {
    "history": 7771,
    "operations": 7772,
    "runner": 7773,
    "strategies": 7774,
    "research": 7775,
    "docs": 7777,
}
DEFAULT_PAGES = {
    "history": "/",
    "operations": "/overview?workspace=1",
    "runner": "/",
    "strategies": "/strategies",
    "research": "/bots?workspace=1",
    "docs": "/",
}
ROUTES = {"/": "history", "/historico": "history", "/operacao": "operations", "/runner": "runner", "/estrategias": "strategies", "/pesquisa": "research", "/documentacao": "docs"}
PANEL_ROUTES = {panel: route for route, panel in ROUTES.items() if route != "/"}
HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"}
ATTRIBUTE_URL = re.compile(r'(?P<attribute>\b(?:href|src|action|poster)\s*=\s*)(?P<quote>["\'])(?P<path>/(?!/)[^"\']*)(?P=quote)', re.IGNORECASE)
CSS_URL = re.compile(r'url\(\s*(?P<quote>["\']?)(?P<path>/(?!/)[^\)"\']+)(?P=quote)\s*\)', re.IGNORECASE)
GATEWAY_PATH = re.compile(r"^/p/([a-z]+)(/.*)?$")


class UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, path: Path) -> None:
        super().__init__("localhost", timeout=20)
        self.path = path

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(str(self.path))


def gateway_url(panel: str, path: str) -> str:
    """Keep upstream URLs inside their own namespace on the new origin."""
    return f"/p/{panel}{path if path.startswith('/') else '/' + path}"


def rewrite_html(body: bytes, panel: str, path: str) -> bytes:
    content = body.decode("utf-8", errors="replace")
    content = ATTRIBUTE_URL.sub(
        lambda match: f"{match.group('attribute')}{match.group('quote')}{gateway_url(panel, match.group('path'))}{match.group('quote')}",
        content,
    )
    content = CSS_URL.sub(
        lambda match: f"url({match.group('quote')}{gateway_url(panel, match.group('path'))}{match.group('quote')})",
        content,
    )
    bridge = f'<script src="/assets/bridge.js" data-panel="{panel}"></script>'
    if not path.startswith("/login"):
        bridge += '<link rel="stylesheet" href="/assets/embedded.css">'
    content, count = re.subn(r"</head\s*>", lambda _: bridge + "</head>", content, count=1, flags=re.IGNORECASE)
    if not count:
        content = bridge + content
    return content.encode("utf-8")


def rewrite_css(body: bytes, panel: str) -> bytes:
    content = body.decode("utf-8", errors="replace")
    return CSS_URL.sub(
        lambda match: f"url({match.group('quote')}{gateway_url(panel, match.group('path'))}{match.group('quote')})",
        content,
    ).encode("utf-8")


def rewrite_location(value: str, panel: str) -> str:
    parsed = urlsplit(value)
    if parsed.netloc and parsed.hostname not in {"127.0.0.1", "localhost"}:
        return value
    target_panel = next((name for name, port in PANELS.items() if str(port) == str(parsed.port)), panel) if parsed.netloc else panel
    path = parsed.path or "/"
    if target_panel in {"operations", "strategies", "research"} and path in {"/", "/workspace"}:
        default = urlsplit(DEFAULT_PAGES[target_panel])
        path = default.path
        query = default.query
    else:
        query = parsed.query
    return urlunsplit(("", "", gateway_url(target_panel, path), query, parsed.fragment))


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        self.dispatch()

    def do_HEAD(self) -> None:
        self.dispatch()

    def do_POST(self) -> None:
        self.dispatch()

    def do_PUT(self) -> None:
        self.dispatch()

    def do_PATCH(self) -> None:
        self.dispatch()

    def do_DELETE(self) -> None:
        self.dispatch()

    def do_OPTIONS(self) -> None:
        self.dispatch()

    def respond(self, status: int, body: bytes, content_type: str, headers: tuple[tuple[str, str], ...] = ()) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        for name, value in headers:
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def dispatch(self) -> None:
        parsed = urlsplit(self.path)
        route = parsed.path.rstrip("/") or "/"
        if self.command in {"GET", "HEAD"} and route in ROUTES:
            self.respond(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8", (("Cache-Control", "no-store"),))
            return
        if self.command in {"GET", "HEAD"} and parsed.path.startswith("/assets/"):
            name = parsed.path.removeprefix("/assets/")
            types = {"app.css": "text/css", "app.js": "text/javascript", "embedded.css": "text/css", "bridge.js": "text/javascript", "lotus-icon.png": "image/png"}
            if name not in types:
                self.send_error(404)
                return
            self.respond(200, (ROOT / "assets" / name).read_bytes(), types[name], (("Cache-Control", "no-cache"),))
            return
        match = GATEWAY_PATH.fullmatch(parsed.path)
        if not match or match.group(1) not in PANELS:
            self.send_error(404)
            return
        panel = match.group(1)
        upstream_path = (match.group(2) or "/") + ("?" + parsed.query if parsed.query else "")
        self.proxy(panel, upstream_path)

    def proxy(self, panel: str, path: str) -> None:
        if panel in {"operations", "strategies", "research"} and urlsplit(path).path == "/workspace" and self.command in {"GET", "HEAD"}:
            self.send_response(303)
            self.send_header("Location", PANEL_ROUTES[panel])
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if panel == "docs":
            self.serve_docs(path)
            return
        port = PANELS[panel]
        length = int(self.headers.get("Content-Length", "0"))
        if length > 16 * 1024 * 1024:
            self.send_error(413)
            return
        payload = self.rfile.read(length) if length else None
        headers = {name: value for name, value in self.headers.items() if name.lower() not in HOP_HEADERS | {"host", "accept-encoding", "content-length"}}
        headers["Host"] = f"127.0.0.1:{port}"
        headers["Accept-Encoding"] = "identity"
        headers["X-Lotus-Gateway"] = "local"
        if payload is not None:
            headers["Content-Length"] = str(len(payload))
        for name in ("Origin", "Referer"):
            if name in headers and headers[name].startswith(f"http://{self.headers.get('Host', '')}"):
                headers[name] = f"http://127.0.0.1:{port}" + headers[name].split(self.headers.get("Host", ""), 1)[1].replace(f"/p/{panel}", "", 1)
        socket_path = SOCKET_DIR / f"gold-lotus-{panel}.sock"
        connection = UnixHTTPConnection(socket_path)
        try:
            connection.request(self.command, path, body=payload, headers=headers)
            upstream = connection.getresponse()
            body = upstream.read()
            content_type = upstream.getheader("Content-Type", "application/octet-stream")
            upstream_headers = upstream.getheaders()
            status = upstream.status
        except (OSError, http.client.HTTPException) as exc:
            self.respond(502, f"O serviço {panel} está indisponível: {exc.__class__.__name__}".encode(), "text/plain; charset=utf-8")
            return
        finally:
            connection.close()
        if "text/html" in content_type and body:
            body = rewrite_html(body, panel, urlsplit(path).path)
        elif "text/css" in content_type and body:
            body = rewrite_css(body, panel)
        self.send_response(status)
        for name, value in upstream_headers:
            lower = name.lower()
            if lower in HOP_HEADERS | {"content-length", "content-encoding", "x-frame-options"}:
                continue
            if lower == "content-security-policy":
                # The gateway is loopback-only and embeds these pages from its own origin.
                value = re.sub(r"(?i)frame-ancestors\s+[^;]+", "frame-ancestors 'self'", value)
            if lower == "location":
                value = rewrite_location(value, panel)
            if lower == "set-cookie":
                # All current panel cookie names are distinct; scope each to its upstream prefix.
                scoped_path = f"Path=/p/{panel}/"
                if re.search(r"(?i)(?:^|;)\s*Path=", value):
                    value = re.sub(r"(?i)Path=[^;]*", scoped_path, value, count=1)
                else:
                    value += "; " + scoped_path
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def serve_docs(self, path: str) -> None:
        if self.command not in {"GET", "HEAD"}:
            self.send_error(405)
            return
        requested = urlsplit(path)
        relative = unquote(requested.path).lstrip("/")
        candidate = (SITE / relative).resolve()
        if not candidate.is_relative_to(SITE.resolve()):
            self.send_error(403)
            return
        if candidate.is_dir():
            if not requested.path.endswith("/"):
                location = gateway_url("docs", requested.path + "/")
                if requested.query:
                    location += "?" + requested.query
                self.send_response(308)
                self.send_header("Location", location)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            candidate /= "index.html"
        if not candidate.is_file():
            self.send_error(404)
            return
        body = candidate.read_bytes()
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        if content_type == "text/html":
            body = rewrite_html(body, "docs", requested.path)
        elif content_type == "text/css":
            body = rewrite_css(body, "docs")
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self.respond(200, body, content_type, (("Cache-Control", "no-cache"),))


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
