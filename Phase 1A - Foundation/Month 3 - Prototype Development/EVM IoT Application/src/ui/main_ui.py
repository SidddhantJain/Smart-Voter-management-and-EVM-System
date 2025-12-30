"""
Main UI for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Navigation between Aadhaar Entry and Biometric Capture screens
"""
from PyQt5.QtWidgets import QApplication, QStackedWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore
from ui.aadhaar_entry import AadhaarEntryScreen
from ui.biometric_capture import BiometricCaptureScreen
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure the `src` directory is in the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

# Adjust the backend path calculation
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

class MainUI(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoteGuard Pro - Main UI")
        self.showFullScreen()
        # Session tracking (for audit correlation only)
        self.session_id = None
        # State machine
        try:
            from voteguard.core.state_machine import State
            self.State = State
            # Treat AADHAAR_ENTRY as idle/ready state in this UI
            self.current_state = State.AADHAAR_ENTRY
        except Exception:
            self.State = None
            self.current_state = None

        # Global shutdown shortcut: Alt+Shift+T
        self.shutdown_shortcut = QShortcut(QKeySequence("Alt+Shift+T"), self)
        self.shutdown_shortcut.setContext(QtCore.Qt.ApplicationShortcut)
        self.shutdown_shortcut.activated.connect(self._shutdown_screen)

        # Initialize screens
        self.aadhaar_screen = AadhaarEntryScreen(self)
        self.biometric_screen = BiometricCaptureScreen(self)
        # Propagate initial (empty) session to children
        if hasattr(self.biometric_screen, 'session_id'):
            self.biometric_screen.session_id = self.session_id

        # Add screens to stacked widget
        self.addWidget(self.aadhaar_screen)
        self.addWidget(self.biometric_screen)

        # Set initial screen
        self.setCurrentIndex(0)

        # Set improved stylesheet for modern look
        self.setStyleSheet("""
            QStackedWidget {
                background-color: #e9ecef;
            }
            QLabel {
                font-size: 32px;
                color: #222;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 600;
                margin-bottom: 16px;
            }
            QLineEdit {
                font-size: 24px;
                padding: 10px;
                border-radius: 6px;
                border: 1px solid #bbb;
                margin-bottom: 16px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 16px 32px;
                font-size: 24px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 500;
                margin: 8px 4px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                transition: background 0.2s;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def _shutdown_screen(self):
        # Gracefully exit the application
        QApplication.instance().quit()

    def navigate_to(self, index: int, target_state):
        """Navigate with state assertion; block invalid transitions."""
        try:
            from voteguard.core.state_machine import assert_transition
            if self.current_state is not None and target_state is not None:
                assert_transition(self.current_state, target_state)
                self.setCurrentIndex(index)
                self.current_state = target_state
                return True
        except Exception:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Navigation Blocked", f"Invalid transition attempted.")
        return False

    def set_state(self, target_state):
        """Update state without changing screen when conceptual step occurs."""
        try:
            from voteguard.core.state_machine import assert_transition
            if self.current_state is not None and target_state is not None:
                assert_transition(self.current_state, target_state)
                self.current_state = target_state
                return True
        except Exception:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "State Blocked", f"Invalid state change attempted.")
        return False

def main():
    app = QApplication([])
    main_ui = MainUI()
    main_ui.show()
    app.exec_()

if __name__ == "__main__":
    main()
