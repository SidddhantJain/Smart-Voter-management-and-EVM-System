import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

try:
    import cv2
except Exception as e:
    raise RuntimeError("OpenCV is required; install opencv-contrib-python") from e

def collect_images(base: Path) -> Tuple[List, List, Dict[int, str]]:
    X = []
    y = []
    labels: Dict[int, str] = {}
    label_id = 0
    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        label_name = entry.name
        labels[label_id] = label_name
        for img_path in sorted(entry.glob("*.jpg")):
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            X.append(img)
            y.append(label_id)
        label_id += 1
    return X, y, labels

def train_and_save(base_dir: str = "imd") -> None:
    base = Path(base_dir)
    if not base.exists():
        raise RuntimeError(f"Image directory {base} not found")

    X, y, labels = collect_images(base)
    if not X:
        raise RuntimeError("No training images found")

    out_dir = Path("voteguard") / "demo" / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "face_recognizer.xml"
    labels_path = out_dir / "labels.json"

    if model_path.exists() and labels_path.exists():
        print(f"Reusing existing model at {model_path}")
        print(f"Reusing existing label map at {labels_path}")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Use numpy array for labels as required by OpenCV 4.x
    recognizer.train(X, np.array(y, dtype=np.int32))

    recognizer.write(str(model_path))
    with labels_path.open("w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)

    print(f"Model written to {model_path}")
    print(f"Label map written to {labels_path}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--imd", default="imd", help="Path to image directory (imd)")
    p.add_argument("--force-retrain", action="store_true", help="Overwrite any existing saved model")
    args = p.parse_args()
    if args.force_retrain:
        out_dir = Path("voteguard") / "demo" / "models"
        model_path = out_dir / "face_recognizer.xml"
        labels_path = out_dir / "labels.json"
        if model_path.exists():
            model_path.unlink()
        if labels_path.exists():
            labels_path.unlink()
    train_and_save(args.imd)
