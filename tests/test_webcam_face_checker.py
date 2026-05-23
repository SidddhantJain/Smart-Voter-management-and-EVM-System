from __future__ import annotations

from scripts.webcam_face_checker import FaceCheckResult, annotate_frame


def test_annotate_frame_handles_valid_and_invalid_states():
    import numpy as np

    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    face_box = (50, 60, 100, 120)

    valid = FaceCheckResult(label="siddhat", confidence=42.0, valid=True)
    annotate_frame(frame, face_box, valid, model_loaded=True)

    invalid = FaceCheckResult(label="unknown", confidence=120.0, valid=False)
    annotate_frame(frame, face_box, invalid, model_loaded=True)

    assert frame.shape == (240, 320, 3)
