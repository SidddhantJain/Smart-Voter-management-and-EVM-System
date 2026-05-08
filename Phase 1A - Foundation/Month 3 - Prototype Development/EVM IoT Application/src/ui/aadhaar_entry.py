"""
Aadhaar Entry Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Aadhaar number input, biometric capture initiation
"""

import os
import sys
import uuid

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QScrollArea,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
)
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
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(18)

        self.form_container = QWidget()
        self.form_container.setMaximumWidth(720)
        form_container_layout = QVBoxLayout(self.form_container)
        form_container_layout.setContentsMargins(32, 24, 32, 24)
        form_container_layout.setSpacing(18)
        form_container_layout.setAlignment(Qt.AlignTop)

        center_row = QHBoxLayout()
        center_row.setContentsMargins(0, 0, 0, 0)
        center_row.setSpacing(0)
        center_row.addStretch(1)
        center_row.addWidget(self.form_container)
        center_row.addStretch(1)

        # Aadhaar Number Input
        self.label = QLabel("Enter your Aadhaar Number:")
        form_container_layout.addWidget(self.label)

        self.aadhaar_input = QLineEdit()
        self.aadhaar_input.setPlaceholderText("Enter 12-digit Aadhaar Number")
        self.aadhaar_input.setMinimumHeight(52)
        form_container_layout.addWidget(self.aadhaar_input)

        # Voter ID Input
        self.voter_id_label = QLabel("Enter your Voter ID:")
        form_container_layout.addWidget(self.voter_id_label)

        self.voter_id_input = QLineEdit()
        self.voter_id_input.setPlaceholderText("Enter Voter ID")
        self.voter_id_input.setMinimumHeight(52)
        form_container_layout.addWidget(self.voter_id_input)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.validate_aadhaar)
        self.submit_button.setMinimumHeight(56)
        form_container_layout.addWidget(self.submit_button)

        form_container_layout.addStretch(1)

        layout.addLayout(center_row)

        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

        self._refresh_form_width()

    def _refresh_form_width(self):
        available_width = max(self.width(), 800)
        form_width = min(720, max(420, int(available_width * 0.55)))
        self.form_container.setFixedWidth(form_width)

    def resizeEvent(self, event):
        self._refresh_form_width()
        super().resizeEvent(event)

    def validate_aadhaar(self):
        aadhaar_number = self.aadhaar_input.text()
        voter_id = self.voter_id_input.text()
        if len(aadhaar_number) == 12 and aadhaar_number.isdigit() and voter_id:
            # Start session (audit correlation only, no PII)
            try:
                session_id = str(uuid.uuid4())
                setattr(self.stacked_widget, "session_id", session_id)
                # Propagate to child screens if present
                if hasattr(self.stacked_widget, "biometric_screen"):
                    self.stacked_widget.biometric_screen.session_id = session_id
                self.audit.log("SESSION_STARTED", {"session_id": session_id})
            except Exception:
                pass
            QMessageBox.information(
                self,
                "Success",
                "Aadhaar and Voter ID Validated. Proceeding to Biometric Capture.",
            )
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
            QMessageBox.warning(
                self,
                "Error",
                "Invalid Aadhaar Number or Voter ID. Please enter valid details.",
            )


if __name__ == "__main__":
    app = QApplication([])
    window = AadhaarEntryScreen()
    window.show()
    app.exec_()
