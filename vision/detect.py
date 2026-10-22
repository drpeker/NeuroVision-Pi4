import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ai_edge_litert.interpreter import Interpreter

MODEL = "models/ssd_mobilenet_v2.tflite"
LABELS = "models/coco_labels.txt"
IMAGE = "/home/drpeker/test.jpg"
OUTPUT = "/home/drpeker/detected.jpg"

interpreter = Interpreter(model_path=MODEL, num_threads=2)
interpreter.allocate_tensors()

inp = interpreter.get_input_details()[0]
outputs = interpreter.get_output_details()

print("Input:", inp["shape"], inp["dtype"])

image = Image.open(IMAGE).convert("RGB")
width, height = image.size

input_height = int(inp["shape"][1])
input_width = int(inp["shape"][2])

resized = image.resize((input_width, input_height))
data = np.asarray(resized, dtype=inp["dtype"])

if np.issubdtype(inp["dtype"], np.floating):
    data = (data.astype(np.float32) - 127.5) / 127.5

data = np.expand_dims(data, axis=0)
interpreter.set_tensor(inp["index"], data)

start = time.perf_counter()
interpreter.invoke()
elapsed = time.perf_counter() - start

boxes = interpreter.get_tensor(outputs[0]["index"])[0]
classes = interpreter.get_tensor(outputs[1]["index"])[0]
scores = interpreter.get_tensor(outputs[2]["index"])[0]
count = int(interpreter.get_tensor(outputs[3]["index"])[0])

labels = {}
with open(LABELS) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and parts[0].isdigit():
            labels[int(parts[0])] = parts[1]

draw = ImageDraw.Draw(image)
found = 0

print("\nNeuroEye - Object Detection")
print("-" * 40)

for i in range(min(count, len(scores))):
    score = float(scores[i])
    if score < 0.10:
        continue

    cls = int(classes[i])
    name = labels.get(cls, f"class {cls}")

    ymin, xmin, ymax, xmax = boxes[i]

    x1 = max(0, min(width, int(xmin * width)))
    y1 = max(0, min(height, int(ymin * height)))
    x2 = max(0, min(width, int(xmax * width)))
    y2 = max(0, min(height, int(ymax * height)))

    if x2 <= x1 or y2 <= y1:
        continue

    draw.rectangle((x1, y1, x2, y2), outline="red", width=3)
    draw.text((x1, max(0, y1 - 14)),
              f"{name} {score:.0%}", fill="yellow")

    print(f"{name}: {score:.1%} [{x1},{y1},{x2},{y2}]")
    found += 1

image.save(OUTPUT)

print(f"\nDetected: {found}")
print(f"Inference: {elapsed:.3f} seconds")
print(f"Saved: {OUTPUT}")
