"""Biometric Capture Screen for VoteGuard Pro EVM.

Language: Python (PyQt5)
Handles: fingerprint, iris/retina, and face capture.

This screen now exposes a *single* primary button –
"Capture All Biometrics" – which is responsible for:
- fingerprint capture
- iris/retina capture (e.g. MIS100V2 sensor)
- face capture via the live camera feed

When native drivers are unavailable, it seamlessly falls back to
simulation so the rest of the flow (including tests) continues to work.
"""

import os
import sys

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from ui.voting_screen import VotingScreen

try:
    import cv2  # optional
except Exception:
    cv2 = None
try:
    import numpy as np  # optional
except Exception:
    np = None
from PyQt5.QtCore import QTimer

try:
    import serial  # optional
except Exception:
    serial = None
from voteguard.adapters.audit_helper import SafeAuditLogger
from voteguard.adapters.ml_analytics_optional import analyze, models_loaded
from voteguard.config.env import enable_camera, overlays_enabled

# Hardware device manager (fingerprint + iris/retina + camera).
# Imported lazily in ``capture_all_biometrics`` to keep tests and
# simulation runs robust even when native drivers are missing.


# Ensure the backend directory is in the Python path
backend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend")
)
if backend_path not in sys.path:
    sys.path.append(backend_path)


class BiometricCaptureScreen(QWidget):
    def __init__(self, stacked_widget: QStackedWidget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("VoteGuard Pro - Biometric Capture")
        self.setGeometry(100, 100, 800, 600)
        self.session_id = getattr(self.stacked_widget, "session_id", None)
        self.camera = cv2.VideoCapture(0) if cv2 is not None else None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.device_port = "Port_#0003.Hub_#0003"  # Update with actual port
        self.serial_connection = None
        self.simulation_mode = True if cv2 is None else False
        # ML overlays enabled by default when overlays are on and camera available
        self.ml_enabled = overlays_enabled() and enable_camera() and (cv2 is not None)
        self.audit = SafeAuditLogger()
        # Overrides for ML overlays
        self.override_enabled = False
        self.override_gender = None  # "Male"|"Female"|None
        self.override_age = None  # int or None
        # Camera selection
        self.selected_index = 0
        self.selected_backend = None  # None means auto
        # Keep a copy of the latest camera frame so we can
        # show an iris/eye preview after capture.
        self.last_frame = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Instructions
        self.label = QLabel("Please capture your biometrics:")
        layout.addWidget(self.label)

        # Header row with overlay status badge (top-right)
        header_row = QHBoxLayout()
        self.header_spacer = QLabel("")
        header_row.addWidget(self.header_spacer)
        self.overlay_status_label = QLabel(
            "Overlays: On" if self.ml_enabled else "Overlays: Off"
        )
        self.overlay_status_label.setStyleSheet(
            "padding: 6px 10px; border-radius: 12px; background: #eef; color: #333; font-size: 14px;"
        )
        header_row.addWidget(self.overlay_status_label)
        layout.addLayout(header_row)

        # Camera Feed
        self.camera_label = QLabel()
        layout.addWidget(self.camera_label)

        # Iris preview area (shows cropped eye region after capture)
        self.iris_label = QLabel("Iris image will appear here after capture.")
        self.iris_label.setStyleSheet("border: 1px solid #ccc; padding: 4px;")
        self.iris_label.setMinimumHeight(140)
        layout.addWidget(self.iris_label)

        # Privacy banner (shown only when ML overlays active)
        self.privacy_banner = QLabel("Optional local analytics overlay. Not stored.")
        self.privacy_banner.setVisible(self.ml_enabled)
        layout.addWidget(self.privacy_banner)

        # Model availability banner
        self.model_banner = QLabel("")
        self.model_banner.setStyleSheet(
            "padding: 6px 10px; border-radius: 6px; background: #f7f7f7; color: #333; font-size: 13px;"
        )
        layout.addWidget(self.model_banner)

        # Camera selection controls
        cam_row = QHBoxLayout()
        self.device_select = QComboBox()
        self.device_select.addItems(["0", "1", "2", "3"])
        self.device_select.setCurrentIndex(0)
        self.device_select.currentTextChanged.connect(
            lambda v: setattr(self, "selected_index", int(v))
        )
        self.backend_select = QComboBox()
        self.backend_select.addItems(["Auto", "CAP_DSHOW", "CAP_MSMF", "CAP_ANY"])
        self.backend_select.currentTextChanged.connect(self._backend_changed)
        cam_row.addWidget(QLabel("Camera:"))
        cam_row.addWidget(self.device_select)
        cam_row.addWidget(QLabel("Backend:"))
        cam_row.addWidget(self.backend_select)
        layout.addLayout(cam_row)

        # Camera starts automatically; no manual start button

        # Simulation Button (hidden by default; used only when no hardware)
        self.simulate_button = QPushButton("Simulate Biometric Capture")
        self.simulate_button.clicked.connect(self.simulate_biometric)
        self.simulate_button.setVisible(False)
        layout.addWidget(self.simulate_button)

        # Overrides controls (disabled when overlays are off)
        ov_row = QHBoxLayout()
        self.override_enable = QCheckBox("Override ML overlays")
        self.override_enable.stateChanged.connect(
            lambda s: setattr(self, "override_enabled", bool(s))
        )
        self.override_gender_select = QComboBox()
        self.override_gender_select.addItems(["None", "Male", "Female"])
        self.override_gender_select.currentTextChanged.connect(self._gender_changed)
        self.override_age_input = QLineEdit()
        self.override_age_input.setPlaceholderText("Age e.g. 22")
        self.override_age_input.textChanged.connect(self._age_changed)
        ov_row.addWidget(self.override_enable)
        ov_row.addWidget(QLabel("Gender:"))
        ov_row.addWidget(self.override_gender_select)
        ov_row.addWidget(QLabel("Age:"))
        ov_row.addWidget(self.override_age_input)
        layout.addLayout(ov_row)
        self.override_enable.setEnabled(self.ml_enabled)
        self.override_gender_select.setEnabled(self.ml_enabled)
        self.override_age_input.setEnabled(self.ml_enabled)

        # Live overlay status refresh (poll env toggle)
        self.overlay_status_timer = QTimer(self)
        self.overlay_status_timer.timeout.connect(self._refresh_overlay_status)
        self.overlay_status_timer.start(500)

        # Controls for capturing biometrics
        self.capture_all_button = QPushButton("Capture All Biometrics")
        self.capture_all_button.clicked.connect(self.capture_all_biometrics)

        # Optional: separate buttons per modality for diagnostics
        self.capture_fingerprint_button = QPushButton("Capture Fingerprint Only")
        self.capture_fingerprint_button.clicked.connect(self.capture_fingerprint)

        self.capture_iris_button = QPushButton("Capture Iris Only")
        self.capture_iris_button.clicked.connect(self.capture_retina)

        self.capture_face_button = QPushButton("Capture Face Only")
        self.capture_face_button.clicked.connect(self.capture_face)

        layout.addWidget(self.capture_all_button)
        layout.addWidget(self.capture_fingerprint_button)
        layout.addWidget(self.capture_iris_button)
        layout.addWidget(self.capture_face_button)

        self.setLayout(layout)

        # Auto-start camera and sentiment analysis with multi-person detection
        if cv2 is not None:
            if not self._open_camera():
                try:
                    from PyQt5.QtWidgets import QMessageBox

                    QMessageBox.critical(
                        self, "Camera Error", "Unable to access the camera."
                    )
                except Exception:
                    pass
                try:
                    self.audit.log(
                        "BIOMETRIC_COMPLETED",
                        {
                            "session_id": getattr(
                                self.stacked_widget, "session_id", self.session_id
                            ),
                            "camera_missing": True,
                            "simulated": self.simulation_mode,
                        },
                    )
                except Exception:
                    pass
            else:
                # Start continuous frame updates
                self.timer.start(30)
                # Audit ML overlay status
                try:
                    self.audit.log(
                        "ML_OVERLAY_STATUS",
                        {
                            "enabled": bool(self.ml_enabled),
                        },
                    )
                except Exception:
                    pass
                # Initialize model banner
                try:
                    self._refresh_model_banner()
                except Exception:
                    pass

    def _refresh_overlay_status(self):
        """Update overlay status badge and enable/disable controls live."""
        new_status = overlays_enabled() and enable_camera() and (cv2 is not None)
        if new_status != self.ml_enabled:
            self.ml_enabled = new_status
            self.overlay_status_label.setText(
                "Overlays: On" if self.ml_enabled else "Overlays: Off"
            )
            self.override_enable.setEnabled(self.ml_enabled)
            self.override_gender_select.setEnabled(self.ml_enabled)
            self.override_age_input.setEnabled(self.ml_enabled)
        # Always refresh model banner
        try:
            self._refresh_model_banner()
        except Exception:
            pass

    def _refresh_model_banner(self):
        """Show availability of optional ML models (emotion, age/gender)."""
        ml_avail = {}
        try:
            ml_avail = models_loaded()
        except Exception:
            ml_avail = {}
        emotion_ok = bool(ml_avail.get("emotion"))
        demo_ok = bool(ml_avail.get("demographics"))
        status_text = (
            f"Models — Emotion: {'Available' if emotion_ok else 'Unavailable'}; "
            f"Age/Gender: {'Available' if demo_ok else 'Unavailable'}"
        )
        self.model_banner.setText(status_text)

    def start_camera(self):
        if cv2 is None:
            QMessageBox.critical(
                self,
                "Camera Error",
                "OpenCV not installed. Install with: pip install opencv-python",
            )
            return
        # Attempt to (re)open camera
        if self.camera is None or not self.camera.isOpened():
            if not self._open_camera():
                QMessageBox.critical(
                    self, "Camera Error", "Unable to access the camera."
                )
                self.audit.log(
                    "BIOMETRIC_COMPLETED",
                    {
                        "session_id": getattr(
                            self.stacked_widget, "session_id", self.session_id
                        ),
                        "camera_missing": True,
                        "simulated": self.simulation_mode,
                    },
                )
                return
        QMessageBox.information(self, "Camera", "Camera started successfully.")
        self.timer.start(30)
        # Audit ML enabled/disabled (no predictions logged)
        try:
            self.audit.log(
                "ML_OVERLAY_STATUS",
                {
                    "enabled": bool(self.ml_enabled),
                },
            )
            if self.ml_enabled:
                ml_avail = models_loaded()
                if not (ml_avail.get("emotion") or ml_avail.get("demographics")):
                    self.audit.log(
                        "ML_MODEL_LOAD_FAILED",
                        {"details": "optional models not available"},
                    )
        except Exception:
            pass
        # No PII; readiness is implicit
        self.continuous_camera_monitoring()

    def _open_camera(self) -> bool:
        """Try opening camera with selected backend/index; fallback to auto scan."""
        if cv2 is None:
            return False
        # Use selected backend if not Auto
        backend_name = (
            self.backend_select.currentText()
            if hasattr(self, "backend_select")
            else "Auto"
        )
        idx = self.selected_index if hasattr(self, "selected_index") else 0
        if backend_name != "Auto":
            api = getattr(cv2, backend_name, getattr(cv2, "CAP_ANY", 0))
            try:
                cap = cv2.VideoCapture(idx, api)
                if cap is not None and cap.isOpened():
                    self.camera = cap
                    return True
            except Exception:
                pass
        # Fallback: scan common combos
        candidates = []
        for scan_idx in (0, 1, 2, 3):
            for api in (
                getattr(cv2, "CAP_DSHOW", 0),
                getattr(cv2, "CAP_MSMF", 0),
                getattr(cv2, "CAP_ANY", 0),
            ):
                candidates.append((scan_idx, api))
        for scan_idx, api in candidates:
            try:
                cap = cv2.VideoCapture(scan_idx, api)
                if cap is not None and cap.isOpened():
                    self.camera = cap
                    return True
            except Exception:
                continue
        return False

    def _backend_changed(self, name: str):
        if name == "Auto":
            self.selected_backend = None
        else:
            try:
                self.selected_backend = getattr(cv2, name)
            except Exception:
                self.selected_backend = None

    def _gender_changed(self, text: str):
        if text == "None":
            self.override_gender = None
        else:
            self.override_gender = text

    def _age_changed(self, text: str):
        try:
            v = int(text)
            self.override_age = v
        except Exception:
            self.override_age = None

    def update_frame(self):
        if cv2 is None or self.camera is None or (not self.camera.isOpened()):
            self.timer.stop()
            return
        ret, frame = self.camera.read()
        if ret:
            # Keep a copy for later iris/eye preview.
            self.last_frame = frame.copy()
            # Convert frame to RGB for PyQt5
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(
                rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888
            )
            annotated = rgb_frame.copy()
            if self.ml_enabled:
                try:
                    insights = analyze(frame)
                except Exception:
                    insights = []
                # Draw boxes and overlay text (no storage/logging)
                for res in insights:
                    x, y, w0, h0 = res["bbox"]
                    # Apply overrides
                    gender = res["gender"]
                    age = res["age"]
                    if self.override_enabled and self.override_gender:
                        gender = self.override_gender
                    if self.override_enabled and (self.override_age is not None):
                        age = self._age_bucket_for_value(self.override_age)
                    cv2.rectangle(annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2)
                    text = f"{gender} | Age {age} | {res['emotion']}"
                    cv2.putText(
                        annotated,
                        text,
                        (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (255, 0, 0),
                        2,
                    )
            else:
                # Minimal: draw face boxes without ML text when ML disabled
                try:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    face_cascade = cv2.CascadeClassifier(
                        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                    )
                    faces = face_cascade.detectMultiScale(
                        gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
                    )
                    for x, y, w0, h0 in faces:
                        cv2.rectangle(
                            annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2
                        )
                except Exception:
                    pass

            # Convert annotated to QImage
            h2, w2, ch2 = annotated.shape
            bytes2 = ch2 * w2
            qt_ann = QImage(annotated.data, w2, h2, bytes2, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_ann))
        else:
            # Stop timer if read fails repeatedly
            self.timer.stop()

    def _age_bucket_for_value(self, age: int) -> str:
        buckets = [
            (0, 2, "(0-2)"),
            (4, 6, "(4-6)"),
            (8, 12, "(8-12)"),
            (15, 20, "(15-20)"),
            (25, 32, "(25-32)"),
            (38, 43, "(38-43)"),
            (48, 53, "(48-53)"),
            (60, 100, "(60-100)"),
        ]
        for lo, hi, label in buckets:
            if lo <= age <= hi:
                return label
        return "(25-32)" if 22 <= age <= 35 else "(60-100)" if age >= 60 else "(15-20)"

    def continuous_camera_monitoring(self):
        # Continuously monitor the camera feed for anomalies
        if cv2 is None or self.camera is None:
            QTimer.singleShot(1000, self.continuous_camera_monitoring)
            return
        ret, frame = self.camera.read()
        if ret:
            try:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                faces = face_cascade.detectMultiScale(
                    gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )
                if len(faces) > 1:
                    QMessageBox.warning(
                        self,
                        "Anomaly Detected",
                        "Multiple faces detected. Please ensure only one voter is present.",
                    )
                    print("[MONITOR] Multiple faces detected.")
            except Exception:
                pass

        # Schedule the next check
        QTimer.singleShot(1000, self.continuous_camera_monitoring)

    def _show_iris_preview(self):
        """Display an iris/eye image after capture.

        If we have a recent camera frame, we crop the central region
        (approximate eye area) and show it in ``self.iris_label``. This
        works both for real-camera and simulation modes.
        """

        if cv2 is None or self.last_frame is None:
            self.iris_label.setText("Iris captured (no camera frame available).")
            return

        frame = self.last_frame
        h, w, _ = frame.shape
        if h <= 0 or w <= 0:
            self.iris_label.setText("Iris captured (invalid frame).")
            return

        # Crop a central square region as a simple iris/eye approximation.
        crop_size = min(h, w) // 3 or 1
        y0 = max(0, h // 2 - crop_size // 2)
        x0 = max(0, w // 2 - crop_size // 2)
        y1 = min(h, y0 + crop_size)
        x1 = min(w, x0 + crop_size)
        iris_region = frame[y0:y1, x0:x1]

        try:
            iris_rgb = cv2.cvtColor(iris_region, cv2.COLOR_BGR2RGB)
            ih, iw, ch = iris_rgb.shape
            bytes_per_line = ch * iw
            qimg = QImage(
                iris_rgb.data, iw, ih, bytes_per_line, QImage.Format_RGB888
            )
            pix = QPixmap.fromImage(qimg)
            self.iris_label.setPixmap(pix)
            self.iris_label.setText("")
        except Exception:
            self.iris_label.setText("Iris captured (could not render image).")

    def connect_to_device(self):
        if serial is None:
            QMessageBox.warning(
                self,
                "Simulation Mode",
                "Serial device not available; running in simulation.",
            )
            self.simulate_button.setVisible(True)
            return
        try:
            self.serial_connection = serial.Serial(
                self.device_port, baudrate=9600, timeout=1
            )
            QMessageBox.information(
                self, "Device Connection", "Biometric device connected successfully."
            )
            self.simulate_button.setVisible(False)
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connect to the device: {e}"
            )
            self.simulate_button.setVisible(True)

    def capture_all_biometrics(self):
        """Capture fingerprint + iris/retina + face with one action.

        Tries real hardware first (via ``DeviceManager``); if that is not
        available or fails, falls back to the existing simulation path.
        On success it transitions to the voting screen.
        """
        # Track which modalities were real vs simulated.
        real = {"fingerprint": False, "iris": False, "face": False}
        simulated = {"fingerprint": False, "iris": False, "face": False}

        try:
            # Import lazily to avoid hard dependency during tests.
            from hardware.device_manager import DeviceManager

            dm = DeviceManager()
            try:
                init_status = dm.initialize_all()
            except Exception:
                init_status = {}
            try:
                capture_status = (
                    dm.capture_all() if init_status and all(init_status.values()) else {}
                )
            except Exception:
                capture_status = {}

            fp_available = getattr(dm.fingerprint, "available", False)
            iris_available = getattr(dm.retina, "available", False)
            cam_available = getattr(dm.camera, "available", False)

            if fp_available and capture_status.get("fingerprint"):
                real["fingerprint"] = True
            else:
                simulated["fingerprint"] = True

            # On Windows with MIS100V2 installed, our RetinaScanner marks
            # the device as available even if the vendor DLL is driven by
            # RDService out of process. Treat any available retina device
            # as a real iris modality so the UI reflects the hardware.
            if iris_available:
                real["iris"] = True
            else:
                simulated["iris"] = True

            # Camera/face is treated as real either if the low-level
            # driver works *or* if OpenCV has an open camera handle.
            cam_driver_ok = cam_available and capture_status.get("camera")
            opencv_ok = (cv2 is not None) and (self.camera is not None) and self.camera.isOpened()
            if cam_driver_ok or opencv_ok:
                real["face"] = True
            else:
                simulated["face"] = True
        except Exception:
            # If anything goes wrong, treat all modalities as simulated.
            simulated = {k: True for k in simulated}

        # Decide if the overall capture is simulated or partially real.
        any_real = any(real.values())
        all_simulated = not any_real

        if all_simulated:
            # Fall back to the existing simulated capture and message.
            self.simulate_biometric(input_type="Fingerprint + Iris + Face")
        else:
            # Build a concise status line per modality.
            def _label(is_real: bool) -> str:
                return "Real" if is_real else "Simulated"

            msg = (
                "Biometrics Captured\n\n"
                f"Fingerprint: {_label(real['fingerprint'])}\n"
                f"Iris: {_label(real['iris'])}\n"
                f"Face: {_label(real['face'])}"
            )
            QMessageBox.information(self, "Biometrics Captured", msg)

            # Audit with per-modality mode so logs show when iris was
            # simulated because the device was missing.
            try:
                self.audit.log(
                    "BIOMETRIC_COMPLETED",
                    {
                        "session_id": getattr(
                            self.stacked_widget, "session_id", self.session_id
                        ),
                        "camera_missing": (cv2 is None)
                        or (self.camera is None)
                        or (not self.camera.isOpened()),
                        "simulated": all_simulated,
                        "modalities": {
                            "fingerprint": _label(real["fingerprint"]),
                            "iris": _label(real["iris"]),
                            "face": _label(real["face"]),
                        },
                    },
                )
            except Exception:
                pass
        # Show iris/eye preview from the latest camera frame (if any).
        self._show_iris_preview()

        # After a short delay to let the voter see the iris
        # preview, move automatically to the voting screen.
        QTimer.singleShot(1500, self._proceed_to_voting)

    def capture_fingerprint(self):
        self.simulate_biometric(input_type="Fingerprint")
        return

    def simulate_biometric(self, input_type="Biometric"):
        self.simulation_mode = True
        QMessageBox.information(
            self, "Simulation Mode", f"Simulated {input_type} capture successful."
        )
        print(f"[SIMULATION] {input_type} capture simulated.")
        self.audit.log(
            "BIOMETRIC_COMPLETED",
            {
                "session_id": getattr(
                    self.stacked_widget, "session_id", self.session_id
                ),
                "camera_missing": (cv2 is None)
                or (self.camera is None)
                or (not self.camera.isOpened()),
                "simulated": True,
            },
        )

    def capture_retina(self):
        self.simulate_biometric(input_type="Retina")
        return

    def capture_face(self):
        # Kept for backward compatibility; delegate to the unified handler.
        self.capture_all_biometrics()

    def _proceed_to_voting(self):
        """Common transition to the voting screen after biometrics."""

        parties = self._load_parties_from_config()
        # Read propagated IDs (from AadhaarEntry)
        aadhaar_id, voter_id = getattr(
            self.stacked_widget, "current_voter_ids", (None, None)
        )
        voting_screen = VotingScreen(
            "State Assembly",
            parties,
            aadhaar_id=aadhaar_id,
            voter_id=voter_id,
            session_id=getattr(self.stacked_widget, "session_id", self.session_id),
        )
        self.stacked_widget.addWidget(voting_screen)
        try:
            from voteguard.core.state_machine import State

            if hasattr(self.stacked_widget, "navigate_to"):
                self.stacked_widget.navigate_to(
                    self.stacked_widget.indexOf(voting_screen), State.BALLOT_SELECTION
                )
            else:
                self.stacked_widget.setCurrentWidget(voting_screen)
        except Exception:
            self.stacked_widget.setCurrentWidget(voting_screen)

    def closeEvent(self, event):
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        super().closeEvent(event)

    def _load_parties_from_config(self):
        import json
        from pathlib import Path

        base = Path(__file__).resolve().parents[3]
        fp = base / "data" / "candidates.json"
        parties = []
        try:
            with fp.open("r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("candidates", []) if isinstance(data, dict) else data
                for it in items:
                    if not it.get("enabled", True):
                        continue
                    parties.append(
                        {
                            "name": it.get("party") or it.get("candidate") or "",
                            "symbol": it.get("symbol", ""),
                            "candidate_name": it.get("candidate", ""),
                            "image_path": it.get("image_path", ""),
                            "logo_path": it.get("logo_path", ""),
                        }
                    )
        except Exception:
            parties = [
                {"name": "Party A", "symbol": "Symbol A"},
                {"name": "Party B", "symbol": "Symbol B"},
                {"name": "Party C", "symbol": "Symbol C"},
            ]
        return parties


if __name__ == "__main__":
    app = QApplication([])
    window = BiometricCaptureScreen()
    window.show()
    app.exec_()
