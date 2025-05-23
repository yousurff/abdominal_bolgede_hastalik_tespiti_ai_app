# utils/image_utils.py

import os, json
import cv2
from datetime import datetime

# Where images go
SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "saved_images")
# Metadata JSON sits next to images
META_PATH = os.path.join(SAVE_DIR, "metadata.json")

def _load_metadata():
    if os.path.isfile(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_metadata(meta: dict):
    os.makedirs(SAVE_DIR, exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def save_image(img_array, name: str, timestamp: datetime, note: str) -> str:
    """
    Saves the image and records its note in metadata.json.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)
    fname = f"{name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    full_path = os.path.join(SAVE_DIR, fname)
    cv2.imwrite(full_path, img_array)

    # record note
    meta = _load_metadata()
    meta[fname] = note
    _save_metadata(meta)

    return full_path