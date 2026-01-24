from __future__ import annotations

from typing import Any, Dict, List

# Optional deps
try:
    import cv2  # type: ignore
except Exception:
    cv2 = None
try:
    import numpy as np  # type: ignore
except Exception:
    np = None

# Optional project ML modules
EmotionRecognizer = None
DemographicsRecognizer = None
try:
    from ml.emotion_recognizer import EmotionRecognizer as _ER  # type: ignore

    EmotionRecognizer = _ER
except Exception:
    pass
try:
    from ml.demographics_recognizer import DemographicsRecognizer as _DR  # type: ignore

    DemographicsRecognizer = _DR
except Exception:
    pass

# In-memory smoothing state (not persisted)
_last_emotions: List[str] = []
_max_buffer = 5


def _smooth_emotion(label: str) -> str:
    try:
        _last_emotions.append(label)
        if len(_last_emotions) > _max_buffer:
            _last_emotions.pop(0)
        # majority vote smoothing
        counts = {}
        for l in _last_emotions:
            counts[l] = counts.get(l, 0) + 1
        return max(counts, key=counts.get)
    except Exception:
        return label


def _detect_faces(frame) -> List[Any]:
    if cv2 is None:
        return []
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        faces = cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        return faces
    except Exception:
        return []


def analyze(frame) -> List[Dict[str, Any]]:
    """Return list of analytics per face: bbox + emotion + age + gender.
    If deps/models missing, returns empty list. Never throws.
    """
    results: List[Dict[str, Any]] = []
    if cv2 is None or np is None:
        return results
    try:
        faces = _detect_faces(frame)
        if not faces:
            return results
        er = EmotionRecognizer() if EmotionRecognizer is not None else None
        dr = DemographicsRecognizer() if DemographicsRecognizer is not None else None
        for x, y, w, h in faces:
            roi = frame[y : y + h, x : x + w]
            emotion_label = "Unknown"
            age_bucket, gender_label = "Unknown", "Unknown"
            try:
                if er is not None:
                    lbl, conf = er.predict(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
                    emotion_label = _smooth_emotion(lbl)
            except Exception:
                emotion_label = "Unknown"
            try:
                if dr is not None:
                    age_bucket, age_conf, gender_label, gender_conf = dr.predict(
                        cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    )
            except Exception:
                age_bucket, gender_label = "Unknown", "Unknown"
            results.append(
                {
                    "bbox": (int(x), int(y), int(w), int(h)),
                    "emotion": emotion_label,
                    "age": age_bucket,
                    "gender": gender_label,
                }
            )
        return results
    except Exception:
        return []


def models_loaded() -> Dict[str, bool]:
    """Indicate availability of optional ML models."""
    return {
        "emotion": EmotionRecognizer is not None,
        "demographics": DemographicsRecognizer is not None,
    }
