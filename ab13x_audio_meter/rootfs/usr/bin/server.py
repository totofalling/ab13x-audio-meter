#!/usr/bin/env python3
import json
import math
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

INPUT = "alsa_input.usb-Generic_AB13X_USB_Audio_20210726905926-00.analog-stereo"
OUTPUT = "alsa_output.usb-Generic_AB13X_USB_Audio_20210726905926-00.analog-stereo"
MONITOR = OUTPUT + ".monitor"
HOST = "0.0.0.0"
PORT = 8765

state = {
    "input_rms": -60.0,
    "input_peak": -60.0,
    "output_rms": -60.0,
    "output_peak": -60.0,
    "input_volume": 0.0,
    "output_volume": 0.0,
    "input_mute": False,
    "output_mute": False,
    "updated": time.time(),
}
lock = threading.Lock()

def pactl(*args):
    return subprocess.check_output(["pactl", *args], text=True, stderr=subprocess.DEVNULL).strip()

def get_volume(kind):
    name = INPUT if kind == "input" else OUTPUT
    out = pactl("get-source-volume" if kind == "input" else "get-sink-volume", name)
    # First percentage occurrence, e.g. 80%
    import re
    m = re.search(r"(\d+(?:\.\d+)?)%", out)
    return float(m.group(1)) if m else 0.0

def get_mute(kind):
    name = INPUT if kind == "input" else OUTPUT
    out = pactl("get-source-mute" if kind == "input" else "get-sink-mute", name)
    return "yes" in out.lower()

def refresh_controls():
    try:
        iv = get_volume("input")
        ov = get_volume("output")
        im = get_mute("input")
        om = get_mute("output")
        with lock:
            state["input_volume"] = round(iv, 1)
            state["output_volume"] = round(ov, 1)
            state["input_mute"] = im
            state["output_mute"] = om
    except Exception:
        pass

def meter_thread(device, rms_key, peak_key):
    while True:
        p = None
        try:
            p = subprocess.Popen([
                "parec", f"--device={device}", "--format=float32le",
                "--rate=16000", "--channels=1", "--raw"
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            chunk = 3200
            while True:
                data = p.stdout.read(chunk * 4)
                if not data:
                    break
                n = len(data) // 4
                if not n:
                    continue
                import struct
                samples = struct.unpack(f"<{n}f", data[:n*4])
                rms = math.sqrt(sum(x*x for x in samples) / n)
                peak = max(abs(x) for x in samples)
                rms_db = 20 * math.log10(max(rms, 1e-9))
                peak_db = 20 * math.log10(max(peak, 1e-9))
                with lock:
                    state[rms_key] = round(max(-60.0, min(0.0, rms_db)), 1)
                    state[peak_key] = round(max(-60.0, min(0.0, peak_db)), 1)
                    state["updated"] = time.time()
        except Exception:
            time.sleep(2)
        finally:
            if p:
                try:
                    p.kill()
                except Exception:
                    pass
        time.sleep(1)

def controls_loop():
    while True:
        refresh_controls()
        time.sleep(1)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(204, {})

    def do_GET(self):
        if self.path == "/state":
            with lock:
                obj = dict(state)
            self.send_json(200, obj)
        elif self.path == "/health":
            self.send_json(200, {"ok": True})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/control":
            self.send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            target = payload.get("target")
            if target not in ("input", "output"):
                raise ValueError("target must be input or output")
            name = INPUT if target == "input" else OUTPUT
            if "volume" in payload:
                value = max(0.0, min(100.0, float(payload["volume"])))
                subprocess.run([
                    "pactl", "set-source-volume" if target == "input" else "set-sink-volume",
                    name, f"{value:.1f}%"
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if "mute" in payload:
                mute = bool(payload["mute"])
                subprocess.run([
                    "pactl", "set-source-mute" if target == "input" else "set-sink-mute",
                    name, "yes" if mute else "no"
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            refresh_controls()
            with lock:
                obj = dict(state)
            self.send_json(200, obj)
        except Exception as exc:
            self.send_json(400, {"error": str(exc)})

if __name__ == "__main__":
    threading.Thread(target=meter_thread, args=(INPUT, "input_rms", "input_peak"), daemon=True).start()
    threading.Thread(target=meter_thread, args=(MONITOR, "output_rms", "output_peak"), daemon=True).start()
    threading.Thread(target=controls_loop, daemon=True).start()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
