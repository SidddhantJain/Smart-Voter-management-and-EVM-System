"""
Aadhaar Entry Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Aadhaar number input, biometric capture initiation
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget
import uuid
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from voteguard.adapters.audit_helper import SafeAuditLogger

class AadhaarEntryScreen(QWidget):
    def __init__(self, stacked_widget: QStackedWidget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("VoteGuard Pro - Aadhaar Entry")
        self.setGeometry(100, 100, 800, 600)
        self.audit = SafeAuditLogger()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Aadhaar Number Input
        self.label = QLabel("Enter your Aadhaar Number:")
        layout.addWidget(self.label)

        self.aadhaar_input = QLineEdit()
        self.aadhaar_input.setPlaceholderText("Enter 12-digit Aadhaar Number")
        layout.addWidget(self.aadhaar_input)

        # Voter ID Input
        self.voter_id_label = QLabel("Enter your Voter ID:")
        layout.addWidget(self.voter_id_label)

        self.voter_id_input = QLineEdit()
        self.voter_id_input.setPlaceholderText("Enter Voter ID")
        layout.addWidget(self.voter_id_input)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.validate_aadhaar)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def validate_aadhaar(self):
        aadhaar_number = self.aadhaar_input.text()
        voter_id = self.voter_id_input.text()
        if len(aadhaar_number) == 12 and aadhaar_number.isdigit() and voter_id:
            # Start session (audit correlation only, no PII)
            try:
                session_id = str(uuid.uuid4())
                setattr(self.stacked_widget, 'session_id', session_id)
                # Propagate to child screens if present
                if hasattr(self.stacked_widget, 'biometric_screen'):
                    self.stacked_widget.biometric_screen.session_id = session_id
                self.audit.log("SESSION_STARTED", {"session_id": session_id})
            except Exception:
                pass
            QMessageBox.information(self, "Success", "Aadhaar and Voter ID Validated. Proceeding to Biometric Capture.")
            # Propagate IDs to the stacked widget so next screen can read them
            self.stacked_widget.current_voter_ids = (aadhaar_number, voter_id)
            # State machine: attempt transition via parent controller
            try:
                from voteguard.core.state_machine import State
                if hasattr(self.stacked_widget, "navigate_to"):
                    self.stacked_widget.navigate_to(1, State.BIOMETRIC_CAPTURE)
                else:
                    self.stacked_widget.setCurrentIndex(1)
            except Exception:
                self.stacked_widget.setCurrentIndex(1)
        else:
            self.audit.log("AADHAAR_VALIDATION_FAILED", {"reason": "format"})
            QMessageBox.warning(self, "Error", "Invalid Aadhaar Number or Voter ID. Please enter valid details.")

if __name__ == "__main__":
    app = QApplication([])
    window = AadhaarEntryScreen()
    window.show()
    app.exec_()
