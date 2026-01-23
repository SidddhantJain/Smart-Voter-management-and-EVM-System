"""
Biometric Capture Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Fingerprint, Retina, and Face Capture
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox, QStackedWidget
from PyQt5.QtWidgets import QFileDialog, QComboBox, QLineEdit, QCheckBox
from ui.voting_screen import VotingScreen
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
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
from voteguard.config.env import enable_camera, enable_ml, overlays_enabled
from voteguard.adapters.ml_analytics_optional import analyze, models_loaded
from voteguard.adapters.audit_helper import SafeAuditLogger

# Ensure the backend directory is in the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

class BiometricCaptureScreen(QWidget):
    def __init__(self, stacked_widget: QStackedWidget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("VoteGuard Pro - Biometric Capture")
        self.setGeometry(100, 100, 800, 600)
        self.session_id = getattr(self.stacked_widget, 'session_id', None)
        self.camera = cv2.VideoCapture(0) if cv2 is not None else None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.device_port = "Port_#0003.Hub_#0003"  # Update with actual port
        self.serial_connection = None
        self.simulation_mode = True if cv2 is None else False
        # Privacy banner for optional ML overlays (respect global overlays toggle)
        self.ml_enabled = overlays_enabled() and enable_camera() and enable_ml() and (cv2 is not None)
        self.audit = SafeAuditLogger()
        # Overrides for ML overlays
        self.override_enabled = False
        self.override_gender = None  # "Male"|"Female"|None
        self.override_age = None     # int or None
        # Camera selection
        self.selected_index = 0
        self.selected_backend = None  # None means auto
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Instructions
        self.label = QLabel("Please capture your biometrics:")
        layout.addWidget(self.label)

        # Camera Feed
        self.camera_label = QLabel()
        layout.addWidget(self.camera_label)

        # Privacy banner (shown only when ML overlays active)
        self.privacy_banner = QLabel("Optional local analytics overlay. Not stored.")
        self.privacy_banner.setVisible(self.ml_enabled)
        layout.addWidget(self.privacy_banner)

        # Camera selection controls
        cam_row = QHBoxLayout()
        self.device_select = QComboBox()
        self.device_select.addItems(["0","1","2","3"])
        self.device_select.setCurrentIndex(0)
        self.device_select.currentTextChanged.connect(lambda v: setattr(self, 'selected_index', int(v)))
        self.backend_select = QComboBox()
        self.backend_select.addItems(["Auto","CAP_DSHOW","CAP_MSMF","CAP_ANY"])
        self.backend_select.currentTextChanged.connect(self._backend_changed)
        cam_row.addWidget(QLabel("Camera:"))
        cam_row.addWidget(self.device_select)
        cam_row.addWidget(QLabel("Backend:"))
        cam_row.addWidget(self.backend_select)
        layout.addLayout(cam_row)

        # Camera starts automatically; no manual start button

        # Test Image (ML) Button
        self.test_image_button = QPushButton("Test Image (ML)")
        self.test_image_button.clicked.connect(self.test_ml_on_image)
        self.test_image_button.setEnabled(cv2 is not None)
        layout.addWidget(self.test_image_button)

        # Fingerprint Capture Button
        self.fingerprint_button = QPushButton("Capture Fingerprint")
        self.fingerprint_button.clicked.connect(self.capture_fingerprint)
        layout.addWidget(self.fingerprint_button)

        # Retina Capture Button
        # Simulation Button (hidden by default)
        self.simulate_button = QPushButton("Simulate Biometric Capture")
        self.simulate_button.clicked.connect(self.simulate_biometric)
        self.simulate_button.setVisible(True)
        layout.addWidget(self.simulate_button)
        self.retina_button = QPushButton("Capture Retina")
        self.retina_button.clicked.connect(self.capture_retina)
        layout.addWidget(self.retina_button)

        # Overrides controls (disabled when overlays are off)
        ov_row = QHBoxLayout()
        self.override_enable = QCheckBox("Override ML overlays")
        self.override_enable.stateChanged.connect(lambda s: setattr(self, 'override_enabled', bool(s)))
        self.override_gender_select = QComboBox()
        self.override_gender_select.addItems(["None","Male","Female"])
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

        # Face Capture Button
        self.face_button = QPushButton("Capture Face")
        self.face_button.clicked.connect(self.capture_face)
        layout.addWidget(self.face_button)

        self.setLayout(layout)

        # Auto-start camera and sentiment analysis with multi-person detection
        if cv2 is not None:
            if not self._open_camera():
                try:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "Camera Error", "Unable to access the camera.")
                except Exception:
                    pass
                try:
                    self.audit.log("BIOMETRIC_COMPLETED", {
                        "session_id": getattr(self.stacked_widget, 'session_id', self.session_id),
                        "camera_missing": True,
                        "simulated": self.simulation_mode,
                    })
                except Exception:
                    pass
            else:
                # Start continuous frame updates
                self.timer.start(30)
                # Audit ML overlay status
                try:
                    self.audit.log("ML_OVERLAY_STATUS", {
                        "enabled": bool(self.ml_enabled),
                    })
                except Exception:
                    pass

    def start_camera(self):
        if cv2 is None:
            QMessageBox.critical(self, "Camera Error", "OpenCV not installed. Install with: pip install opencv-python")
            return
        # Attempt to (re)open camera
        if self.camera is None or not self.camera.isOpened():
            if not self._open_camera():
                QMessageBox.critical(self, "Camera Error", "Unable to access the camera.")
                self.audit.log("BIOMETRIC_COMPLETED", {
                    "session_id": getattr(self.stacked_widget, 'session_id', self.session_id),
                    "camera_missing": True,
                    "simulated": self.simulation_mode,
                })
                return
        QMessageBox.information(self, "Camera", "Camera started successfully.")
        self.timer.start(30)
        # Audit ML enabled/disabled (no predictions logged)
        try:
            self.audit.log("ML_OVERLAY_STATUS", {
                "enabled": bool(self.ml_enabled),
            })
            if self.ml_enabled:
                ml_avail = models_loaded()
                if not (ml_avail.get("emotion") or ml_avail.get("demographics")):
                    self.audit.log("ML_MODEL_LOAD_FAILED", {"details": "optional models not available"})
        except Exception:
            pass
        # No PII; readiness is implicit
        self.continuous_camera_monitoring()

    def _open_camera(self) -> bool:
        """Try opening camera with selected backend/index; fallback to auto scan."""
        if cv2 is None:
            return False
        # Use selected backend if not Auto
        backend_name = self.backend_select.currentText() if hasattr(self, 'backend_select') else "Auto"
        idx = self.selected_index if hasattr(self, 'selected_index') else 0
        if backend_name != "Auto":
            api = getattr(cv2, backend_name, getattr(cv2, 'CAP_ANY', 0))
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
            for api in (getattr(cv2, 'CAP_DSHOW', 0), getattr(cv2, 'CAP_MSMF', 0), getattr(cv2, 'CAP_ANY', 0)):
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

    def test_ml_on_image(self):
        if cv2 is None:
            QMessageBox.critical(self, "ML Error", "OpenCV not installed. Install with: pip install opencv-python")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select image", "", "Images (*.png *.jpg *.jpeg);;All Files (*.*)")
        if not path:
            return
        try:
            img = cv2.imread(path)
            if img is None:
                raise ValueError("Failed to read image")
            annotated = img.copy()
            insights = []
            try:
                insights = analyze(img)
            except Exception:
                insights = []
            for res in insights:
                (x, y, w0, h0) = res.get("bbox", (0,0,0,0))
                cv2.rectangle(annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2)
                text = f"{res.get('gender','?')} | Age {res.get('age','?')} | {res.get('emotion','?')}"
                cv2.putText(annotated, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)
            rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_img))
            QMessageBox.information(self, "ML Test", f"Processed {len(insights)} face(s).")
        except Exception as e:
            QMessageBox.critical(self, "ML Test Error", str(e))

    def update_frame(self):
        if cv2 is None or self.camera is None or (not self.camera.isOpened()):
            self.timer.stop()
            return
        ret, frame = self.camera.read()
        if ret:
            # Convert frame to RGB for PyQt5
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            annotated = rgb_frame.copy()
            if self.ml_enabled:
                try:
                    insights = analyze(frame)
                except Exception:
                    insights = []
                # Draw boxes and overlay text (no storage/logging)
                for res in insights:
                    (x, y, w0, h0) = res["bbox"]
                    # Apply overrides
                    gender = res['gender']
                    age = res['age']
                    if self.override_enabled and self.override_gender:
                        gender = self.override_gender
                    if self.override_enabled and (self.override_age is not None):
                        age = self._age_bucket_for_value(self.override_age)
                    cv2.rectangle(annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2)
                    text = f"{gender} | Age {age} | {res['emotion']}"
                    cv2.putText(annotated, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)
            else:
                # Minimal: draw face boxes without ML text when ML disabled
                try:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
                    for (x, y, w0, h0) in faces:
                        cv2.rectangle(annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2)
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
            (0, 2, "(0-2)"), (4, 6, "(4-6)"), (8, 12, "(8-12)"), (15, 20, "(15-20)"),
            (25, 32, "(25-32)"), (38, 43, "(38-43)"), (48, 53, "(48-53)"), (60, 100, "(60-100)")
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
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                if len(faces) > 1:
                    QMessageBox.warning(self, "Anomaly Detected", "Multiple faces detected. Please ensure only one voter is present.")
                    print("[MONITOR] Multiple faces detected.")
            except Exception:
                pass

        # Schedule the next check
        QTimer.singleShot(1000, self.continuous_camera_monitoring)

    def connect_to_device(self):
        if serial is None:
            QMessageBox.warning(self, "Simulation Mode", "Serial device not available; running in simulation.")
            self.simulate_button.setVisible(True)
            return
        try:
            self.serial_connection = serial.Serial(self.device_port, baudrate=9600, timeout=1)
            QMessageBox.information(self, "Device Connection", "Biometric device connected successfully.")
            self.simulate_button.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to the device: {e}")
            self.simulate_button.setVisible(True)

    def capture_fingerprint(self):
        self.simulate_biometric(input_type="Fingerprint")
        return

    def simulate_biometric(self, input_type="Biometric"):
        self.simulation_mode = True
        QMessageBox.information(self, "Simulation Mode", f"Simulated {input_type} capture successful.")
        print(f"[SIMULATION] {input_type} capture simulated.")
        self.audit.log("BIOMETRIC_COMPLETED", {
            "session_id": getattr(self.stacked_widget, 'session_id', self.session_id),
            "camera_missing": (cv2 is None) or (self.camera is None) or (not self.camera.isOpened()),
            "simulated": True,
        })

    def capture_retina(self):
        self.simulate_biometric(input_type="Retina")
        return

    def capture_face(self):
        self.simulate_biometric(input_type="Face")
        # Transition to Voting Screen
        parties = [
            {"name": "Party A", "symbol": "Symbol A"},
            {"name": "Party B", "symbol": "Symbol B"},
            {"name": "Party C", "symbol": "Symbol C"},
            {"name": "Party D", "symbol": "Symbol D"},
            {"name": "Party E", "symbol": "Symbol E"},
        ]
        # Read propagated IDs (from AadhaarEntry)
        aadhaar_id, voter_id = getattr(self.stacked_widget, 'current_voter_ids', (None, None))
        voting_screen = VotingScreen("State Assembly", parties, aadhaar_id=aadhaar_id, voter_id=voter_id, session_id=getattr(self.stacked_widget, 'session_id', self.session_id))
        self.stacked_widget.addWidget(voting_screen)
        try:
            from voteguard.core.state_machine import State
            if hasattr(self.stacked_widget, "navigate_to"):
                self.stacked_widget.navigate_to(self.stacked_widget.indexOf(voting_screen), State.BALLOT_SELECTION)
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

if __name__ == "__main__":
    app = QApplication([])
    window = BiometricCaptureScreen()
    window.show()
    app.exec_()
