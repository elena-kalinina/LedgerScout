#!/usr/bin/env python3
"""Serve the canvas AND stream a live mission run to it, step by step.

    python3 scripts/serve.py                # http://localhost:8000/frontend/canvas.html

Two things on one origin:
  * static files (the canvas + recorded logs), and
  * GET /api/run?scenario=knitwear&live=1&delay=0.6  → a Server-Sent Events stream.

The canvas's "▶ Run live" button opens that SSE endpoint; each agent event is pushed as
it happens and the canvas fills in step by step. With live=1 the run creates real
(test-mode) Stripe charges as the payment steps are revealed.
"""
import json
import os
import queue
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ledger_scout.missions import research  # noqa: E402

_DONE = object()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if urlparse(self.path).path == "/api/run":
            return self._stream_run(parse_qs(urlparse(self.path).query))
        return super().do_GET()

    def _stream_run(self, qs):
        scenario = qs.get("scenario", ["knitwear"])[0]
        live = qs.get("live", ["0"])[0] == "1"
        delay = max(0.0, min(2.0, float(qs.get("delay", ["0.6"])[0])))
        if scenario not in research.SCENARIOS:
            self.send_error(404, f"unknown scenario {scenario!r}")
            return

        # Toggle the payment rail for this run. The live-key guard still refuses sk_live_.
        os.environ["LEDGERSCOUT_STRIPE_LIVE"] = "1" if live else "0"

        # Stream until the run finishes, then close the socket (the body is delimited by
        # connection close). The browser's EventSource also closes itself on the 'done'
        # event; closing here keeps non-streaming clients and "network idle" happy.
        self.protocol_version = "HTTP/1.1"
        self.close_connection = True
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        q: "queue.Queue" = queue.Queue()

        def on_emit(ev):
            q.put(ev)
            time.sleep(delay)  # pace the actual run so the canvas reveals it step by step

        def worker():
            try:
                research.run(scenario=scenario, on_emit=on_emit)
            except Exception as exc:  # surface backend errors (e.g. live-key guard) to the UI
                q.put({"kind": "error", "actor": "server", "text": str(exc)})
            finally:
                q.put(_DONE)

        threading.Thread(target=worker, daemon=True).start()

        try:
            while True:
                ev = q.get()
                if ev is _DONE:
                    self.wfile.write(b"event: done\ndata: {}\n\n")
                    self.wfile.flush()
                    return
                self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass  # client navigated away / closed the stream

    def log_message(self, *args):  # keep the console clean for the demo
        pass


def main():
    port = int(os.getenv("PORT", "8000"))
    url = f"http://localhost:{port}/frontend/canvas.html"
    print("Ledger Scout — canvas + live stream")
    print(f"  open:  {url}")
    print("  then click ▶ Run live (step by step) on the canvas.")
    print("  Ctrl-C to stop.")
    try:
        ThreadingHTTPServer(("", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
