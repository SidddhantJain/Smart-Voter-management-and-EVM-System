"""
Demographics recognizer for age and gender using OpenCV DNN or ONNXRuntime.
Looks for:
- Caffe models: models/deploy_age.prototxt + models/age_net.caffemodel
                models/deploy_gender.prototxt + models/gender_net.caffemodel
- OR single ONNX: models/age_gender.onnx (expects outputs [age_logits, gender_logits])
Falls back to Unknown when models are not present.
"""
from pathlib import Path
from typing import Tuple, Optional

import numpy as np

try:
    import onnxruntime as ort  # type: ignore
except Exception:
    ort = None


class DemographicsRecognizer:
    AGE_BUCKETS = ["(0-2)", "(4-6)", "(8-12)", "(15-20)", "(25-32)", "(38-43)", "(48-53)", "(60-100)"]

    def __init__(self):
        repo_root = Path(__file__).resolve().parents[4]
        self.models_dir = repo_root / "models"
        self.age_proto = self.models_dir / "deploy_age.prototxt"
        self.age_model = self.models_dir / "age_net.caffemodel"
        self.gender_proto = self.models_dir / "deploy_gender.prototxt"
        self.gender_model = self.models_dir / "gender_net.caffemodel"
        self.age_gender_onnx = self.models_dir / "age_gender.onnx"

        self.age_net = None
        self.gender_net = None
        self.ort_sess = None

        try:
            import cv2
            if self.age_proto.exists() and self.age_model.exists():
                self.age_net = cv2.dnn.readNetFromCaffe(str(self.age_proto), str(self.age_model))
            if self.gender_proto.exists() and self.gender_model.exists():
                self.gender_net = cv2.dnn.readNetFromCaffe(str(self.gender_proto), str(self.gender_model))
        except Exception:
            self.age_net = None
            self.gender_net = None

        if ort is not None and self.age_gender_onnx.exists():
            try:
                self.ort_sess = ort.InferenceSession(str(self.age_gender_onnx), providers=["CPUExecutionProvider"])  # type: ignore
            except Exception:
                self.ort_sess = None

        # If no models available, try auto-download Caffe age/gender models
        if not self.available():
            self._ensure_models_downloaded()
            try:
                import cv2
                if self.age_proto.exists() and self.age_model.exists():
                    self.age_net = cv2.dnn.readNetFromCaffe(str(self.age_proto), str(self.age_model))
                if self.gender_proto.exists() and self.gender_model.exists():
                    self.gender_net = cv2.dnn.readNetFromCaffe(str(self.gender_proto), str(self.gender_model))
            except Exception:
                self.age_net = None
                self.gender_net = None

    def available(self) -> bool:
        return any([self.age_net is not None, self.gender_net is not None, self.ort_sess is not None])

    def predict(self, face_rgb: np.ndarray) -> Tuple[str, float, str, float]:
        """Returns (age_bucket, age_conf, gender_label, gender_conf)."""
        try:
            import cv2
            blob = cv2.dnn.blobFromImage(face_rgb, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
        except Exception:
            return ("Unknown", 0.0, "Unknown", 0.0)

        # ONNX path if available
        if self.ort_sess is not None:
            try:
                age_out, gender_out = self.ort_sess.run(None, {self.ort_sess.get_inputs()[0].name: blob})  # type: ignore
                age_probs = self._softmax(age_out.squeeze())
                gender_probs = self._softmax(gender_out.squeeze())
                age_idx = int(np.argmax(age_probs))
                gender_idx = int(np.argmax(gender_probs))
                return (self.AGE_BUCKETS[age_idx], float(age_probs[age_idx]), ["Male", "Female"][gender_idx], float(gender_probs[gender_idx]))
            except Exception:
                pass

        # Caffe path
        age_bucket = "Unknown"
        age_conf = 0.0
        gender_label = "Unknown"
        gender_conf = 0.0
        try:
            import cv2
            if self.age_net is not None:
                self.age_net.setInput(blob)
                age_preds = self.age_net.forward().squeeze()
                age_idx = int(np.argmax(age_preds))
                age_bucket = self.AGE_BUCKETS[age_idx]
                age_conf = float(age_preds[age_idx])
            if self.gender_net is not None:
                self.gender_net.setInput(blob)
                gender_preds = self.gender_net.forward().squeeze()
                gender_idx = int(np.argmax(gender_preds))
                gender_label = ["Male", "Female"][gender_idx]
                gender_conf = float(gender_preds[gender_idx])
        except Exception:
            pass

        return (age_bucket, age_conf, gender_label, gender_conf)

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        exps = np.exp(logits - np.max(logits))
        return exps / np.sum(exps)

    def _ensure_models_downloaded(self) -> None:
        urls = {
            self.age_proto: "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/models/deploy_age.prototxt",
            self.age_model: "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/models/age_net.caffemodel",
            self.gender_proto: "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/models/deploy_gender.prototxt",
            self.gender_model: "https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/models/gender_net.caffemodel",
        }
        try:
            import requests  # type: ignore
            self.models_dir.mkdir(parents=True, exist_ok=True)
            for path, url in urls.items():
                if not path.exists():
                    resp = requests.get(url, timeout=20)
                    if resp.status_code == 200:
                        path.write_bytes(resp.content)
        except Exception:
            # Fallback to urllib if requests isn't available
            try:
                import urllib.request
                self.models_dir.mkdir(parents=True, exist_ok=True)
                for path, url in urls.items():
                    if not path.exists():
                        with urllib.request.urlopen(url, timeout=20) as resp:  # type: ignore
                            data = resp.read()
                            path.write_bytes(data)
            except Exception:
                pass
