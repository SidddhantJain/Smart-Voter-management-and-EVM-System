"""
Main UI for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Navigation between Aadhaar Entry and Biometric Capture screens
"""
from PyQt5.QtWidgets import QApplication, QStackedWidget
from aadhaar_entry import AadhaarEntryScreen
from biometric_capture import BiometricCaptureScreen
import sys
import os

# Correct the backend path calculation
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

class MainUI(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoteGuard Pro - Main UI")
        self.setGeometry(100, 100, 800, 600)

        # Initialize screens
        self.aadhaar_screen = AadhaarEntryScreen(self)
        self.biometric_screen = BiometricCaptureScreen(self)

        # Add screens to stacked widget
        self.addWidget(self.aadhaar_screen)
        self.addWidget(self.biometric_screen)

        # Set initial screen
        self.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication([])
    main_ui = MainUI()
    main_ui.show()
    app.exec_()
