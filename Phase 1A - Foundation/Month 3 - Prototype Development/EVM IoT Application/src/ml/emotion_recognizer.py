"""
Emotion recognition using optional ONNXRuntime with FER+ model.
If `models/ferplus.onnx` is present, runs inference; otherwise returns 'Unknown'.
"""
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

try:
    import onnxruntime as ort  # type: ignore
except Exception:  # pragma: no cover
    ort = None  # Fallback when onnxruntime isn't available


EMOTIONS = [
    "Neutral",
    "Happiness",
    "Surprise",
    "Sadness",
    "Anger",
    "Disgust",
    "Fear",
    "Contempt",
]


class EmotionRecognizer:
    def __init__(self, model_path: Optional[Path] = None):
        # Default model path: repo_root/models/ferplus.onnx
        if model_path is None:
            repo_root = Path(__file__).resolve().parents[4]
            model_path = repo_root / "models" / "ferplus.onnx"

        self.model_path = model_path
        self.session = None
        if ort is not None and model_path.exists():
            try:
                self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])  # type: ignore
            except Exception:
                self.session = None

    def available(self) -> bool:
        return self.session is not None

    def _preprocess(self, face_rgb: np.ndarray) -> np.ndarray:
        """
        Convert face ROI (RGB) to 64x64 grayscale normalized tensor of shape (1,1,64,64).
        """
        import cv2

        gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
        resized = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
        norm = resized.astype(np.float32) / 255.0
        tensor = norm[np.newaxis, np.newaxis, :, :]  # (1,1,64,64)
        return tensor

    def predict(self, face_rgb: np.ndarray) -> Tuple[str, float]:
        """
        Returns (emotion_label, confidence). Falls back to ('Unknown', 0.0).
        """
        if self.session is None:
            return ("Unknown", 0.0)

        inp = self._preprocess(face_rgb)
        try:
            outputs = self.session.run(None, {self.session.get_inputs()[0].name: inp})  # type: ignore
            logits = outputs[0].squeeze()  # assume first output
            # Softmax
            exps = np.exp(logits - np.max(logits))
            probs = exps / np.sum(exps)
            idx = int(np.argmax(probs))
            return (EMOTIONS[idx], float(probs[idx]))
        except Exception:
            return ("Unknown", 0.0)
