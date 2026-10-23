import io
import json
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
from PIL import Image, ImageDraw
import cv2
from ai_edge_litert.interpreter import Interpreter

MODEL = "vision/models/ssd_mobilenet_v2.tflite"
LABELS = "vision/models/coco_labels.txt"
THRESHOLD = 0.40
PORT = 8080

labels = {}
with open(LABELS) as f:
    for line in f:
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2 and parts[0].isdigit():
            labels[int(parts[0])] = parts[1]

interpreter = Interpreter(model_path=MODEL, num_threads=2)
interpreter.allocate_tensors()
inp = interpreter.get_input_details()[0]
outs = interpreter.get_output_details()

camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)

if not camera.isOpened():
    raise RuntimeError("Logitech C270 kamerasi acilamadi")

time.sleep(1)

latest_jpeg = None
latest_detections = []
latest_timestamp = None
latest_raw_jpeg = None
lock = threading.Lock()
running = True

def vision_loop():
    global latest_jpeg, latest_detections, latest_timestamp, latest_raw_jpeg

    while running:
        ok, frame = camera.read()
        if not ok:
            time.sleep(0.1)
            continue
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        width, height = image.size

        resized = image.resize(
            (int(inp["shape"][2]), int(inp["shape"][1]))
        )
        data = np.asarray(resized, dtype=inp["dtype"])
        if np.issubdtype(inp["dtype"], np.floating):
            data = (data.astype(np.float32) - 127.5) / 127.5

        interpreter.set_tensor(
            inp["index"], np.expand_dims(data, axis=0)
        )

        interpreter.invoke()

        boxes = interpreter.get_tensor(outs[0]["index"])[0]
        classes = interpreter.get_tensor(outs[1]["index"])[0]
        scores = interpreter.get_tensor(outs[2]["index"])[0]
        count = int(interpreter.get_tensor(outs[3]["index"])[0])

        raw_buffer = io.BytesIO()
        image.save(raw_buffer, format='JPEG', quality=80)
        raw_jpeg = raw_buffer.getvalue()

        draw = ImageDraw.Draw(image)
        detections = []

        for i in range(min(count, len(scores))):
            score = float(scores[i])
            if score < THRESHOLD:
                continue

            cls = int(classes[i])
            name = labels.get(cls, f"class_{cls}")
            ymin, xmin, ymax, xmax = boxes[i]

            x1 = max(0, min(width, int(xmin * width)))
            y1 = max(0, min(height, int(ymin * height)))
            x2 = max(0, min(width, int(xmax * width)))
            y2 = max(0, min(height, int(ymax * height)))

            if x2 <= x1 or y2 <= y1:
                continue

            draw.rectangle(
                (x1, y1, x2, y2),
                outline="red", width=3
            )
            draw.text(
                (x1, max(0, y1 - 14)),
                f"{name} {score:.0%}",
                fill="yellow"
            )

            detections.append({
                "class": name,
                "confidence": round(score, 3),
                "box": [x1, y1, x2, y2]
            })

        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=70)

        with lock:
            latest_jpeg = buf.getvalue()
            latest_detections = detections
            latest_raw_jpeg = raw_jpeg
            latest_timestamp = time.time()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/snapshot":
            with lock:
                jpg = latest_raw_jpeg
            if jpg is None:
                self.send_error(503, "Frame not ready")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(jpg)))
            self.end_headers()
            self.wfile.write(jpg)
            return

        if self.path == "/scene":
            with lock:
                timestamp = latest_timestamp
                objects = list(latest_detections)
            age = None if timestamp is None else round(time.time() - timestamp, 2)
            scene = {
                "source": "NeuroVision Live",
                "timestamp": timestamp,
                "age_seconds": age,
                "ready": timestamp is not None,
                "fresh": age is not None and age <= 5,
                "objects": objects
            }
            payload = json.dumps(scene).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/detections":
            with lock:
                payload = json.dumps(latest_detections).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/":
            html = b"""<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width">
<title>NeuroEye Live</title></head>
<body style="background:#111;color:white;text-align:center;
font-family:Arial">
<h2>NeuroEye - Live Vision AI</h2>
<img src="/stream" style="width:95%;max-width:800px">
<p>Raspberry Pi 4 / Logitech C270 / SSD MobileNet V2</p>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html)
            return

        if self.path == "/stream":
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "multipart/x-mixed-replace; boundary=frame"
            )
            self.end_headers()

            try:
                while running:
                    with lock:
                        jpg = latest_jpeg

                    if jpg:
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(
                            b"Content-Type: image/jpeg\r\n\r\n"
                        )
                        self.wfile.write(jpg)
                        self.wfile.write(b"\r\n")
                        self.wfile.flush()

                    time.sleep(0.2)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        self.send_error(404)

thread = threading.Thread(target=vision_loop, daemon=True)
thread.start()

server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

print(f"NeuroEye LIVE: http://neurobrain.local:{PORT}")

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    running = False
    server.server_close()
    thread.join(timeout=3)
    camera.release()
