# models/object_detector.py

from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# figure out where to load best.pt from (dev vs. frozen)
if getattr(sys, "frozen", False):
    # PyInstaller has unpacked data here
    base_dir = sys._MEIPASS
else:
    # running in your source tree
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
model_path = os.path.join(base_dir, "models", "best.pt")
model      = YOLO(model_path)
class_map = model.names

class_colors = {
    0: (0, 255, 0),     # green
    1: (255, 0, 0),     # red
    2: (0, 0, 255),     # blue
    3: (255, 255, 0),   # yellow
    4: (255, 0, 255),   # magenta
    5: (0, 255, 255),   # cyan
    6: (128, 128, 0),   # olive
}

# --- locate and load Montserrat font safely ---
# __file__ is …/aht_app/models/object_detector.py
BASE_DIR     = os.path.dirname(__file__)
RESOURCES    = os.path.abspath(os.path.join(BASE_DIR, "..", "resources"))
FONT_FILE    = os.path.join(RESOURCES, "Montserrat-Regular.ttf")

try:
# scale factor
    SCALE = 0.7

# reduced sizes
    large_size = max(1, int(32 * SCALE))
    small_size = max(1, int(20))

    FONT_LARGE = ImageFont.truetype(FONT_FILE, large_size)
    FONT_SMALL = ImageFont.truetype(FONT_FILE, small_size)
except Exception as e:
    print(f"⚠️  Could not load Montserrat font ({FONT_FILE}): {e}")
    # fallback to PIL default
    FONT_LARGE = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()


def detect_objects(image_path: str):
    # … read & run inference …
    bgr = cv2.imread(image_path)
    results = model(bgr)[0]

    # collect *indices*
    detected_idxs = { int(b.cls[0].item()) for b in results.boxes }

    # build header text
    header = ", ".join(class_map[i] for i in sorted(detected_idxs))

    # pick color of the *first* detected disease
    if detected_idxs:
        idx0 = next(iter(detected_idxs))
        color = class_colors.get(idx0, (0,255,0))
    else:
        color = (0,255,0)

    # convert to PIL, draw header in that color
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    draw    = ImageDraw.Draw(pil_img)

    if header:
        draw.text(
            (10, 10), 
            header, 
            font=FONT_LARGE, 
            fill=(color[0], color[1], color[2], 255)
        )

    # now draw each box + per‐box label in *its* class color
    for b in results.boxes:
        idx       = int(b.cls[0].item())
        label     = class_map[idx]
        box_color = class_colors.get(idx, (0,255,0))
        x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())

        # rectangle
        draw.rectangle(
            [(x1, y1), (x2, y2)],
            outline=(box_color[0], box_color[1], box_color[2], 255),
            width=2
        )

        # measure label size
        bbox = draw.textbbox((0,0), label, font=FONT_SMALL)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        ty   = y1 - h - 4
        if ty < 0:
            ty = y1 + 4


    # convert back to OpenCV and return…

    # 5) back to OpenCV
    out_rgb = np.array(pil_img)
    out_bgr = cv2.cvtColor(out_rgb, cv2.COLOR_RGB2BGR)
    return out_bgr, results.boxes