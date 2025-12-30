"""
Biometric Capture Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Fingerprint, Retina, and Face Capture
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QStackedWidget
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
try:
    from ml.emotion_recognizer import EmotionRecognizer
except Exception:
    EmotionRecognizer = None
try:
    from ml.demographics_recognizer import DemographicsRecognizer
except Exception:
    DemographicsRecognizer = None
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
        self.emotion = EmotionRecognizer() if EmotionRecognizer is not None else None
        self.demo = DemographicsRecognizer() if DemographicsRecognizer is not None else None
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

        # Start Camera Button
        self.start_camera_button = QPushButton("Start Camera")
        self.start_camera_button.clicked.connect(self.start_camera)
        self.start_camera_button.setEnabled(cv2 is not None)
        layout.addWidget(self.start_camera_button)

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
        if cv2 is None or self.camera is None or not self.camera.isOpened():
            QMessageBox.critical(self, "Camera Error", "Unable to access the camera.")
            self.audit.log("BIOMETRIC_COMPLETED", {
                "session_id": getattr(self.stacked_widget, 'session_id', self.session_id),
                "camera_missing": True,
                "simulated": self.simulation_mode,
            })
            return
        self.timer.start(30)
        # No PII; readiness is implicit
        self.continuous_camera_monitoring()

    def update_frame(self):
        if cv2 is None or self.camera is None:
            return
        ret, frame = self.camera.read()
        if ret:
            # Convert frame to RGB for PyQt5
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Detect faces and annotate
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

            annotated = rgb_frame.copy()
            for (x, y, w0, h0) in faces:
                # Draw rectangle
                cv2.rectangle(annotated, (x, y), (x + w0, y + h0), (0, 255, 0), 2)
                # Emotion prediction
                face_roi = annotated[y:y + h0, x:x + w0]
                label, conf = (self.emotion.predict(face_roi) if self.emotion is not None else ("Unknown", 0.0))
                # Age/Gender
                if self.demo is not None:
                    age_bucket, age_conf, gender_label, gender_conf = self.demo.predict(face_roi)
                else:
                    age_bucket, age_conf, gender_label, gender_conf = ("Unknown", 0.0, "Unknown", 0.0)
                text = f"{gender_label} {gender_conf:.2f} | Age {age_bucket} {age_conf:.2f} | {label} {conf:.2f}"
                cv2.putText(annotated, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)

            # Convert annotated to QImage
            h2, w2, ch2 = annotated.shape
            bytes2 = ch2 * w2
            qt_ann = QImage(annotated.data, w2, h2, bytes2, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_ann))

    def continuous_camera_monitoring(self):
        # Continuously monitor the camera feed for anomalies
        if cv2 is None or self.camera is None:
            QTimer.singleShot(1000, self.continuous_camera_monitoring)
            return
        ret, frame = self.camera.read()
        if ret:
            # Example: Detect multiple faces
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 1:
                QMessageBox.warning(self, "Anomaly Detected", "Multiple faces detected. Please ensure only one voter is present.")
                print("[MONITOR] Multiple faces detected.")
            elif len(faces) == 1:
                # Optional: log primary face emotion
                (x, y, w0, h0) = faces[0]
                face_rgb = cv2.cvtColor(frame[y:y + h0, x:x + w0], cv2.COLOR_BGR2RGB)
                label, conf = (self.emotion.predict(face_rgb) if self.emotion is not None else ("Unknown", 0.0))
                if self.demo is not None:
                    age_bucket, age_conf, gender_label, gender_conf = self.demo.predict(face_rgb)
                else:
                    age_bucket, age_conf, gender_label, gender_conf = ("Unknown", 0.0, "Unknown", 0.0)
                print(f"[EMOTION] {label} ({conf:.2f}) | [AGE] {age_bucket} ({age_conf:.2f}) | [GENDER] {gender_label} ({gender_conf:.2f})")

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
