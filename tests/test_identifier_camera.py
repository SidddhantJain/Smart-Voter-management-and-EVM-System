"""Camera + identifier integration test.

Runs a quick live-check: opens the default camera, searches for a face
using OpenCV Haar cascade, and if a trained LBPH recognizer exists under
`voteguard/demo/models/face_recognizer.xml` it will attempt a prediction.

This test is intended as a manual/integration test and will `pytest.skip`
when no camera is available.
"""
from __future__ import annotations

import time
from pathlib import Path
import json

import pytest


def _open_camera(index: int = 0, timeout: float = 5.0):
    import cv2

    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else 0)
    t0 = time.time()
    while not cap.isOpened() and (time.time() - t0) < timeout:
        time.sleep(0.1)
    if not cap.isOpened():
        cap.release()
        return None
    return cap


def test_camera_and_identifier_opens_and_detects_face():
    try:
        import cv2
    except Exception:
        pytest.skip("OpenCV not installed")

    cap = _open_camera()
    if cap is None:
        pytest.skip("No camera available or cannot open device")

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    found_face = False
    recognizer_used = False
    recognizer_prediction = None

    # try for a few frames to find a face
    for _ in range(40):
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.05)
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(80, 80))
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_img = gray[y : y + h, x : x + w]
            found_face = True
            # try to use demo recognizer if present
            try:
                from voteguard.demo.biometric import SimulatedBiometricWorkflow

                sw = SimulatedBiometricWorkflow()
                rec = getattr(sw, "_recognizer", None)
                labels = getattr(sw, "_labels", {}) or {}
                if rec is not None:
                    # LBPH expects a single-channel image; resize to a reasonable size
                    face_small = cv2.resize(face_img, (200, 200))
                    label, conf = rec.predict(face_small)
                    recognizer_used = True
                    recognizer_prediction = (label, conf, labels.get(str(label)))
            except Exception:
                # ignore recognizer issues; the core test is camera+face detection
                pass
            break
        time.sleep(0.05)

    cap.release()

    assert found_face, "Camera opened but no face was detected in the frames"
    if recognizer_used:
        assert isinstance(recognizer_prediction, tuple) and len(recognizer_prediction) >= 2
        # If labels.json was produced by training, ensure expected label exists
        labels_path = Path("voteguard") / "demo" / "models" / "labels.json"
        if labels_path.exists():
            with labels_path.open("r", encoding="utf-8") as fh:
                labels_map = json.load(fh)
            assert any(v == "siddhat" for v in labels_map.values()), "Expected label 'siddhat' not found in trained labels"
