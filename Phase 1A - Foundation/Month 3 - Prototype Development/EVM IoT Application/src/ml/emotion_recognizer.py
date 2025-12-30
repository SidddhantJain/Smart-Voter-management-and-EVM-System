"""
Emotion recognition using optional ONNXRuntime with FER+ model.
If `models/ferplus.onnx` is present, runs inference; otherwise returns 'Unknown'.
"""
import os
from pathlib import Path
from typing import Optional, Tuple
from collections import deque, Counter

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
        # History buffer for temporal smoothing
        self._history = deque(maxlen=7)  # (label, conf) for recent frames
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
            # Fallback: simple smile detection using Haar cascade
            try:
                import cv2
                gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
                smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
                smiles = smile_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=25)
                if len(smiles) > 0:
                    return self._smooth("Happiness", 0.6)
                else:
                    return self._smooth("Neutral", 0.5)
            except Exception:
                return self._smooth("Unknown", 0.0)

        inp = self._preprocess(face_rgb)
        try:
            outputs = self.session.run(None, {self.session.get_inputs()[0].name: inp})  # type: ignore
            logits = outputs[0].squeeze()  # assume first output
            # Softmax
            exps = np.exp(logits - np.max(logits))
            probs = exps / np.sum(exps)
            idx = int(np.argmax(probs))
            label = EMOTIONS[idx]
            conf = float(probs[idx])
            # If low confidence, try smile fallback
            if conf < 0.35:
                try:
                    import cv2
                    gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
                    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
                    smiles = smile_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=25)
                    if len(smiles) > 0:
                        return self._smooth("Happiness", 0.6)
                except Exception:
                    pass
            return self._smooth(label, conf)
        except Exception:
            return self._smooth("Unknown", 0.0)

    def _smooth(self, label: str, conf: float) -> Tuple[str, float]:
        """
        Apply temporal smoothing using a short history window.
        Majority vote for label; average confidence for the majority label.
        """
        self._history.append((label, conf))
        if not self._history:
            return label, conf
        labels = [l for l, _ in self._history]
        counts = Counter(labels)
        majority_label, majority_count = counts.most_common(1)[0]
        # Require at least 3 occurrences in window to override current label
        if majority_count >= 3:
            confs = [c for l, c in self._history if l == majority_label]
            avg_conf = float(sum(confs) / max(len(confs), 1))
            return majority_label, avg_conf
        return label, conf
