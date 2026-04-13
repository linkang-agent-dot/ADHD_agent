#!/usr/bin/env python3
"""Get GRFal session cookie via Chrome CDP or manual fallback.

Launches Chrome with remote debugging, waits for DingTalk login,
extracts session cookie automatically. Falls back to manual paste.

Usage:
    python get_grfal_cookie.py
    python get_grfal_cookie.py --config path/to/config.json
    python get_grfal_cookie.py --url http://172.20.90.45:6018
"""

import argparse
import base64
import hashlib
import json
import os
import socket
import struct
import subprocess
import sys
import time
import urllib.request
import urllib.error


CHROME_PATHS_WIN = [
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

CHROME_PATHS_MAC = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

DEBUG_PORT = 9222
DEFAULT_URL = "http://172.20.90.45:6018"


# ---------------------------------------------------------------------------
# Minimal WebSocket client (stdlib only, for single CDP request/response)
# ---------------------------------------------------------------------------

def _ws_connect(host, port, path):
    sock = socket.create_connection((host, port), timeout=10)
    key = base64.b64encode(os.urandom(16)).decode()
    handshake = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(handshake.encode())

    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk

    status_line = resp.split(b"\r\n")[0]
    if b"101" not in status_line:
        sock.close()
        raise ConnectionError(f"WebSocket handshake failed: {status_line.decode(errors='replace')}")

    return sock


def _ws_send(sock, data):
    payload = data.encode("utf-8")
    frame = bytearray()
    frame.append(0x81)

    mask_key = os.urandom(4)
    length = len(payload)

    if length < 126:
        frame.append(0x80 | length)
    elif length < 65536:
        frame.append(0x80 | 126)
        frame.extend(struct.pack(">H", length))
    else:
        frame.append(0x80 | 127)
        frame.extend(struct.pack(">Q", length))

    frame.extend(mask_key)
    masked = bytearray(b ^ mask_key[i % 4] for i, b in enumerate(payload))
    frame.extend(masked)
    sock.sendall(frame)


def _ws_recv(sock):
    def _read_exact(n):
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(min(4096, n - len(buf)))
            if not chunk:
                raise ConnectionError("WebSocket connection closed")
            buf += chunk
        return buf

    header = _read_exact(2)
    is_masked = bool(header[1] & 0x80)
    length = header[1] & 0x7F

    if length == 126:
        length = struct.unpack(">H", _read_exact(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", _read_exact(8))[0]

    mask = _read_exact(4) if is_masked else None
    data = _read_exact(length)

    if mask:
        data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))

    return data.decode("utf-8")


def cdp_get_cookies(ws_url):
    """Get all browser cookies via Chrome DevTools Protocol."""
    # ws://host:port/devtools/page/ID
    url_body = ws_url.replace("ws://", "")
    host_port, path = url_body.split("/", 1)
    host, port = host_port.split(":")

    sock = _ws_connect(host, int(port), "/" + path)
    try:
        cmd = json.dumps({"id": 1, "method": "Network.getAllCookies"})
        _ws_send(sock, cmd)

        while True:
            msg = _ws_recv(sock)
            parsed = json.loads(msg)
            if parsed.get("id") == 1:
                return parsed.get("result", {}).get("cookies", [])
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Chrome management
# ---------------------------------------------------------------------------

def find_chrome():
    paths = CHROME_PATHS_WIN if sys.platform == "win32" else CHROME_PATHS_MAC
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def launch_chrome(url, port=DEBUG_PORT):
    chrome = find_chrome()
    if not chrome:
        return None

    temp_dir = os.path.join(
        os.environ.get("TEMP", os.environ.get("TMPDIR", "/tmp")),
        "grfal_chrome_profile",
    )
    os.makedirs(temp_dir, exist_ok=True)

    args = [
        chrome,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        url,
    ]

    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


def get_cdp_pages(port=DEBUG_PORT, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(f"http://localhost:{port}/json/list")
            with urllib.request.urlopen(req, timeout=3) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(1)
    return None


def extract_grfal_cookie(cookies, grfal_host):
    """Build cookie string from CDP cookies matching GRFal host."""
    host_clean = grfal_host.replace("http://", "").replace("https://", "").split(":")[0]
    matched = [c for c in cookies if host_clean in c.get("domain", "")]
    if not matched:
        matched = cookies

    parts = []
    for c in matched:
        parts.append(f"{c['name']}={c['value']}")
    return "; ".join(parts)


# ---------------------------------------------------------------------------
# Config I/O
# ---------------------------------------------------------------------------

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config_path, config):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Get GRFal session cookie")
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"),
        help="Path to config.json (default: ../config.json relative to script)",
    )
    parser.add_argument("--url", default=None, help="GRFal URL override")
    parser.add_argument("--port", type=int, default=DEBUG_PORT, help="Chrome debug port")
    args = parser.parse_args()

    config = load_config(args.config)
    grfal_url = args.url or config.get("grfal_url", DEFAULT_URL)

    print(f"GRFal URL: {grfal_url}")
    print(f"Config:    {args.config}")

    # --- Attempt 1: Chrome CDP auto-extraction ---
    chrome_path = find_chrome()
    if chrome_path:
        print(f"\nChrome found: {chrome_path}")
        print(f"Launching with remote debugging on port {args.port}...")

        proc = launch_chrome(grfal_url, args.port)
        if proc:
            print("\n" + "=" * 50)
            print("  Please complete DingTalk login in the browser.")
            print("  After login succeeds, press ENTER here.")
            print("=" * 50)

            try:
                input("\n>>> Press ENTER after login... ")
            except (EOFError, KeyboardInterrupt):
                proc.terminate()
                print("\nCancelled.")
                sys.exit(1)

            pages = get_cdp_pages(args.port)
            if pages:
                ws_url = pages[0].get("webSocketDebuggerUrl")
                if ws_url:
                    try:
                        cookies = cdp_get_cookies(ws_url)
                        cookie_str = extract_grfal_cookie(cookies, grfal_url)
                        if cookie_str:
                            config["grfal_cookie"] = cookie_str
                            save_config(args.config, config)
                            print(f"\nCookie extracted and saved! ({len(cookies)} cookies)")
                            print(f"Saved to: {args.config}")
                            proc.terminate()
                            return
                        else:
                            print("No cookies found. Falling back to manual.")
                    except Exception as e:
                        print(f"CDP cookie extraction failed: {e}")
                        print("Falling back to manual.")

            proc.terminate()
    else:
        print("Chrome not found. Using manual mode.")
        import webbrowser
        webbrowser.open(grfal_url)

    # --- Attempt 2: Manual cookie paste ---
    print("\n" + "=" * 50)
    print("  Manual Cookie Extraction")
    print("=" * 50)
    print(f"\n1. Open {grfal_url} in browser and login")
    print("2. Press F12 -> Network tab -> Refresh page")
    print("3. Click any request -> Headers -> Copy 'Cookie' value")
    print("4. Paste below:\n")

    try:
        cookie = input("Cookie: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        sys.exit(1)

    if not cookie:
        print("No cookie provided. Exiting.")
        sys.exit(1)

    config["grfal_cookie"] = cookie
    save_config(args.config, config)
    print(f"\nCookie saved to: {args.config}")


if __name__ == "__main__":
    main()
