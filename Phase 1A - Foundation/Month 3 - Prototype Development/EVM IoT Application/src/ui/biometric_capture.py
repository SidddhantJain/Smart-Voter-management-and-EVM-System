"""
Biometric Capture Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Fingerprint, Retina, and Face Capture
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QStackedWidget
from voting_screen import VotingScreen
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import cv2
import numpy as np
from PyQt5.QtCore import QTimer

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
            self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

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

        # Schedule the next check
        QTimer.singleShot(1000, self.continuous_camera_monitoring)

    def capture_fingerprint(self):
        # Simulate capturing a fingerprint and saving it as an image
        fingerprint_image_path = "captured_fingerprint.jpg"
        cv2.imwrite(fingerprint_image_path, np.zeros((100, 100), dtype=np.uint8))  # Placeholder for actual fingerprint image
        QMessageBox.information(self, "Fingerprint Capture", f"Fingerprint captured and saved as '{fingerprint_image_path}'.")
        print(f"[UI] Fingerprint captured and saved as '{fingerprint_image_path}'.")

    def capture_retina(self):
        # Simulate integration with retina scanner
        QMessageBox.information(self, "Retina Capture", "Retina captured successfully.")
        print("[UI] Retina capture simulated.")

    def capture_face(self):
        ret, frame = self.camera.read()
        if not ret:
            QMessageBox.critical(self, "Capture Error", "Unable to capture face.")
            return

        # Load Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            QMessageBox.warning(self, "Face Detection", "No face detected. Please try again.")
            return

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imwrite("captured_face.jpg", frame)
        QMessageBox.information(self, "Face Capture", "Face captured successfully and saved as 'captured_face.jpg'.")
        # Transition to Voting Screen
        parties = [
            {"name": "Party A", "symbol": "Symbol A"},
            {"name": "Party B", "symbol": "Symbol B"},
            {"name": "Party C", "symbol": "Symbol C"},
            {"name": "Party D", "symbol": "Symbol D"},
            {"name": "Party E", "symbol": "Symbol E"},
        ]
        voting_screen = VotingScreen("State Assembly", parties)
        self.stacked_widget.addWidget(voting_screen)
        self.stacked_widget.setCurrentWidget(voting_screen)

    def closeEvent(self, event):
        self.timer.stop()
        self.camera.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = BiometricCaptureScreen()
    window.show()
    app.exec_()
