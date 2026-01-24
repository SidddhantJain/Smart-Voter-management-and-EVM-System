"""
Emotion recognition using optional ONNXRuntime with FER+ model.
If `models/ferplus.onnx` is present, runs inference; otherwise uses a simple
heuristic fallback (neutral/happiness). Auto-downloads FER+ ONNX if missing.
"""

import os
from collections import Counter, deque
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

try:
    import onnxruntime as ort  # type: ignore
except Exception:  # pragma: no cover
    ort = None  # Fallback when onnxruntime isn't available

# Optional fallback via DeepFace if ONNX model isn't available
try:
    from deepface import DeepFace  # type: ignore
except Exception:
    DeepFace = None  # type: ignore


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
        # Default model path: repo_root/Phase 1A - Foundation/models/ferplus.onnx
        if model_path is None:
            repo_root = Path(__file__).resolve().parents[4]
            model_path = repo_root / "Phase 1A - Foundation" / "models" / "ferplus.onnx"

        self.model_path = model_path
        self.session = None
        # History buffer for temporal smoothing
        self._history = deque(maxlen=5)  # (label, conf) for recent frames
        # Ensure model is available (auto-download if missing)
        if not model_path.exists():
            self._ensure_model_downloaded(model_path)
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
        Returns (emotion_label, confidence).
        If ONNX model is unavailable, uses a simple heuristic fallback.
        """
        if self.session is None:
            # Fallback: smile vs neutral. We avoid over-classifying happiness.
            try:
                # Try DeepFace first if available
                if DeepFace is not None:
                    try:
                        # DeepFace expects BGR by default; convert RGB->BGR
                        import cv2

                        face_bgr = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR)
                        res = DeepFace.analyze(face_bgr, actions=["emotion"], enforce_detection=False)  # type: ignore
                        if isinstance(res, list) and res:
                            res = res[0]
                        label = str(res.get("dominant_emotion", "Neutral")).capitalize()
                        return self._smooth(
                            label, float(res.get("emotion", {}).get(label.lower(), 0.6))
                        )
                    except Exception:
                        pass
                # Otherwise, simple smile/neutral heuristic
                import cv2

                gray = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2GRAY)
                smile_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_smile.xml"
                )
                smiles = smile_cascade.detectMultiScale(
                    gray, scaleFactor=1.3, minNeighbors=40
                )
                if len(smiles) > 0:
                    return self._smooth("Happiness", 0.60)
                return self._smooth("Neutral", 0.55)
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
        # Require at least 2 occurrences in window to override current label
        if majority_count >= 2:
            confs = [c for l, c in self._history if l == majority_label]
            avg_conf = float(sum(confs) / max(len(confs), 1))
            return majority_label, avg_conf
        return label, conf

    def _ensure_model_downloaded(self, model_path: Path) -> None:
        """Download FER+ ONNX model if not present."""
        urls = [
            # ONNX official models repo
            "https://github.com/onnx/models/raw/main/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx",
            # Alternate mirror (if needed)
            "https://raw.githubusercontent.com/onnx/models/main/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx",
        ]
        try:
            models_dir = model_path.parent
            models_dir.mkdir(parents=True, exist_ok=True)
            for url in urls:
                try:
                    import requests  # type: ignore

                    resp = requests.get(url, timeout=30)
                    if resp.status_code == 200 and resp.content:
                        model_path.write_bytes(resp.content)
                        break
                except Exception:
                    import urllib.request

                    with urllib.request.urlopen(url, timeout=30) as r:  # type: ignore
                        data = r.read()
                        if data:
                            model_path.write_bytes(data)
                            break
        except Exception:
            # Leave as-is; fallback path will handle gracefully
            pass
