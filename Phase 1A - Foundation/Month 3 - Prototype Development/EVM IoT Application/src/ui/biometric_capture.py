"""
Biometric Capture Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Fingerprint, Retina, and Face Capture
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QStackedWidget
from PyQt5.QtWidgets import QFileDialog
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
from voteguard.config.env import enable_camera, enable_ml
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
        # Privacy banner for optional ML overlays
        self.ml_enabled = enable_camera() and enable_ml() and (cv2 is not None)
        self.audit = SafeAuditLogger()
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

        # Start Camera Button
        self.start_camera_button = QPushButton("Start Camera")
        self.start_camera_button.clicked.connect(self.start_camera)
        self.start_camera_button.setEnabled(cv2 is not None)
        layout.addWidget(self.start_camera_button)

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

        # Face Capture Button
        self.face_button = QPushButton("Capture Face")
        self.face_button.clicked.connect(self.capture_face)
        layout.addWidget(self.face_button)

        self.setLayout(layout)

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
        """Try opening camera with multiple backends and indices (Windows-friendly)."""
        if cv2 is None:
            return False
        candidates = []
        # Try indices 0-3 with common Windows APIs
        for idx in (0, 1, 2, 3):
            for api in (getattr(cv2, 'CAP_DSHOW', 0), getattr(cv2, 'CAP_MSMF', 0), getattr(cv2, 'CAP_ANY', 0)):
                candidates.append((idx, api))
        for idx, api in candidates:
            try:
                cap = cv2.VideoCapture(idx, api)
                if cap is not None and cap.isOpened():
                    self.camera = cap
                    return True
            except Exception:
                continue
        return False

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
                    cv2.rectangle(annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2)
                    text = f"{res['gender']} | Age {res['age']} | {res['emotion']}"
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
