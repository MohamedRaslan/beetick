"""Serve this demo over http:// and open it in a browser.

    python demo/serve.py

Standard library only, so it needs no virtual environment or install.

Everything in the demo works by opening `demo/index.html` directly, with one
exception: Playwright's trace viewer refuses to load over file:// and asks to be
served. Running this script is the easiest way to get the trace open.
"""

from __future__ import annotations

import argparse
import http.server
import webbrowser
from functools import partial
from pathlib import Path


# Served from the repository root so links out of the demo into the source tree
# resolve the same way they do when the page is opened from disk.
REPO_ROOT = Path(__file__).resolve().parent.parent


class _ReusableServer(http.server.ThreadingHTTPServer):
    # Lets the port be reclaimed immediately after a restart.
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the B.TECH automation demo.")
    parser.add_argument("--port", type=int, default=8000, help="default: 8000")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="do not open a browser window",
    )
    args = parser.parse_args()

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(REPO_ROOT))

    with _ReusableServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://127.0.0.1:{args.port}/demo/"
        print(f"Demo:    {url}")
        print("Stop:    Ctrl+C")

        if not args.no_browser:
            webbrowser.open(url)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
