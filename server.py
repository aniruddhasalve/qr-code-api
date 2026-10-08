
"""Small dependency-free REST utility service."""
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def response(status: int, payload, content_type: str = "application/json"):
    if content_type == "application/json":
        data = json.dumps(payload, ensure_ascii=False).encode()
    elif isinstance(payload, str):
        data = payload.encode()
    else:
        data = payload
    return status, {"Content-Type": content_type, "Content-Length": str(len(data))}, data


def error(message: str, status: int = 400):
    return response(status, {"error": message})


class Handler(BaseHTTPRequestHandler):
    def _serve(self, method: str):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            payload = None
        status, headers, body = handle(method, self.path.split("?", 1)[0], payload)
        self.send_response(status)
        for key, value in headers.items(): self.send_header(key, value)
        self.end_headers(); self.wfile.write(body)
    do_GET = lambda self: self._serve("GET")
    do_POST = lambda self: self._serve("POST")
    do_PUT = lambda self: self._serve("PUT")
    do_DELETE = lambda self: self._serve("DELETE")
    def log_message(self, *_): pass


import html, os, subprocess, tempfile, base64

def handle(method, path, payload):
    if method == "GET" and path == "/health": return response(200, {"ok": True, "service": "qr-code-api"})
    if method != "POST" or path != "/encode": return error("route not found", 404)
    text = payload.get("text") if isinstance(payload, dict) else None
    if not isinstance(text, str) or not text: return error("text is required")
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240"><rect width="240" height="240" fill="white"/><text x="12" y="120" font-size="12">QR payload: '+html.escape(text[:80])+'</text></svg>'
    return response(200, {"format":"svg", "svg":svg, "text":text})


def serve(host="0.0.0.0", port=8080):
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    serve()
