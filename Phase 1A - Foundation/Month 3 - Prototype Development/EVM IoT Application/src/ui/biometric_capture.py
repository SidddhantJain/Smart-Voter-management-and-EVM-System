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
import cv2
import numpy as np
from PyQt5.QtCore import QTimer
import serial
from ml.emotion_recognizer import EmotionRecognizer

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
        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.device_port = "Port_#0003.Hub_#0003"  # Update with actual port
        self.serial_connection = None
        self.simulation_mode = False
        self.emotion = EmotionRecognizer()  # optional ONNX
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
        layout.addWidget(self.start_camera_button)

        # Fingerprint Capture Button
        self.fingerprint_button = QPushButton("Capture Fingerprint")
        self.fingerprint_button.clicked.connect(self.capture_fingerprint)
        layout.addWidget(self.fingerprint_button)

        # Retina Capture Button
        # Simulation Button (hidden by default)
        self.simulate_button = QPushButton("Simulate Biometric Capture")
        self.simulate_button.clicked.connect(self.simulate_biometric)
        self.simulate_button.setVisible(False)
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
        if not self.camera.isOpened():
            QMessageBox.critical(self, "Camera Error", "Unable to access the camera.")
            return
        self.timer.start(30)
        self.continuous_camera_monitoring()

    def update_frame(self):
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
                label, conf = self.emotion.predict(face_roi)
                text = f"{label} ({conf:.2f})" if conf > 0 else label
                cv2.putText(annotated, text, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Convert annotated to QImage
            h2, w2, ch2 = annotated.shape
            bytes2 = ch2 * w2
            qt_ann = QImage(annotated.data, w2, h2, bytes2, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_ann))

    def continuous_camera_monitoring(self):
        # Continuously monitor the camera feed for anomalies
        ret, frame = self.camera.read()
        if ret:
            # Example: Detect multiple faces
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 1:
                QMessageBox.warning(self, "Anomaly Detected", "Multiple faces detected. Please ensure only one voter is present.")
                print("[MONITOR] Multiple faces detected.")
            elif len(faces) == 1 and self.emotion.available():
                # Optional: log primary face emotion
                (x, y, w0, h0) = faces[0]
                face_rgb = cv2.cvtColor(frame[y:y + h0, x:x + w0], cv2.COLOR_BGR2RGB)
                label, conf = self.emotion.predict(face_rgb)
                print(f"[EMOTION] Primary face: {label} ({conf:.2f})")

        # Schedule the next check
        QTimer.singleShot(1000, self.continuous_camera_monitoring)

    def connect_to_device(self):
        try:
            self.serial_connection = serial.Serial(self.device_port, baudrate=9600, timeout=1)
            QMessageBox.information(self, "Device Connection", "Biometric device connected successfully.")
            self.simulate_button.setVisible(False)
        except serial.SerialException as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to the device: {e}")
            self.simulate_button.setVisible(True)

    def capture_fingerprint(self):
        self.simulate_biometric(input_type="Fingerprint")
        return

    def simulate_biometric(self, input_type="Biometric"):
        self.simulation_mode = True
        QMessageBox.information(self, "Simulation Mode", f"Simulated {input_type} capture successful.")
        print(f"[SIMULATION] {input_type} capture simulated.")

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
        voting_screen = VotingScreen("State Assembly", parties, aadhaar_id=aadhaar_id, voter_id=voter_id)
        self.stacked_widget.addWidget(voting_screen)
        self.stacked_widget.setCurrentWidget(voting_screen)

    def closeEvent(self, event):
        self.timer.stop()
        self.camera.release()
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = BiometricCaptureScreen()
    window.show()
    app.exec_()
