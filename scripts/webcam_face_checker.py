"""Webcam face checker for VoteGuard Pro.

Opens the webcam, detects faces, and draws a green box when the face
matches the trained label and a red box otherwise. If the LBPH model is
not present, the app still shows detected faces and marks them as
"NO MODEL".

Typical usage:
    python scripts/webcam_face_checker.py --expected-label siddhat

The app is intentionally small and interactive so you can visually confirm
that the camera and recognition pipeline are working.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import cv2
except Exception as exc:  # pragma: no cover - environment dependent
    cv2 = None
    _CV2_IMPORT_ERROR = exc
else:
    _CV2_IMPORT_ERROR = None


@dataclass(frozen=True)
class FaceCheckResult:
    label: str
    confidence: Optional[float]
    valid: bool


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_model(model_dir: Path) -> Tuple[Optional[object], Dict[int, str]]:
    model_path = model_dir / "face_recognizer.xml"
    labels_path = model_dir / "labels.json"
    if not model_path.exists() or not labels_path.exists():
        return None, {}

    if cv2 is None:
        return None, {}
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(model_path))
    with labels_path.open("r", encoding="utf-8") as fh:
        raw = json.load(fh)
    labels = {int(k): str(v) for k, v in raw.items()}
    return recognizer, labels


def open_camera(index: int = 0, timeout_seconds: float = 5.0) -> Optional[cv2.VideoCapture]:
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    start = time.time()
    while time.time() - start < timeout_seconds:
        for backend in backends:
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                return cap
            cap.release()
        time.sleep(0.1)
    return None


def detect_faces(frame_bgr):
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    return face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)), gray


def predict_face(recognizer, labels: Dict[int, str], gray_face, expected_label: str) -> FaceCheckResult:
    face_resized = cv2.resize(gray_face, (200, 200))
    label_id, confidence = recognizer.predict(face_resized)
    predicted = labels.get(int(label_id), f"label_{label_id}")
    valid = predicted.lower() == expected_label.lower() and confidence <= 80.0
    return FaceCheckResult(label=predicted, confidence=float(confidence), valid=valid)


def annotate_frame(frame_bgr, face_box, result: FaceCheckResult, model_loaded: bool) -> None:
    x, y, w, h = face_box
    color = (0, 200, 0) if result.valid else (0, 0, 255)
    cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), color, 2)
    status = "VALID" if result.valid else ("INVALID" if model_loaded else "NO MODEL")
    confidence = f"{result.confidence:.1f}" if result.confidence is not None else "-"
    text = f"{status}: {result.label} ({confidence})"
    text_y = y - 10 if y - 10 > 20 else y + h + 25
    cv2.putText(frame_bgr, text, (x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)


def main() -> int:
    parser = argparse.ArgumentParser(description="Open webcam and show valid/invalid face boxes")
    parser.add_argument("--expected-label", default="siddhat", help="Label name that should be treated as valid")
    parser.add_argument("--camera-index", type=int, default=0, help="Webcam index")
    parser.add_argument("--model-dir", default=str(repo_root() / "voteguard" / "demo" / "models"), help="Directory containing face_recognizer.xml and labels.json")
    args = parser.parse_args()

    if cv2 is None:
        print("[Error] OpenCV is not installed in this environment.")
        print("Install it with: python -m pip install opencv-contrib-python")
        return 1

    recognizer, labels = load_model(Path(args.model_dir))
    cap = open_camera(args.camera_index)
    if cap is None:
        print("[Error] Could not open webcam")
        return 1

    print("[Info] Webcam started. Press q to quit.")
    if recognizer is None:
        print("[Warn] Model not found. Face boxes will be shown as NO MODEL.")
    else:
        print(f"[Info] Loaded model labels: {sorted(set(labels.values()))}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            faces, gray = detect_faces(frame)
            if len(faces) == 0:
                cv2.putText(frame, "No face detected", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            for face in faces:
                x, y, w, h = face
                gray_face = gray[y : y + h, x : x + w]
                if recognizer is None:
                    result = FaceCheckResult(label="unknown", confidence=None, valid=False)
                else:
                    result = predict_face(recognizer, labels, gray_face, args.expected_label)
                annotate_frame(frame, face, result, recognizer is not None)
            cv2.imshow("VoteGuard Webcam Face Checker", frame)
            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
