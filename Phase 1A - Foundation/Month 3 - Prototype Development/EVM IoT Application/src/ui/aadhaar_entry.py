"""
Aadhaar Entry Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Aadhaar number input, biometric capture initiation
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedWidget

class AadhaarEntryScreen(QWidget):
    def __init__(self, stacked_widget: QStackedWidget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("VoteGuard Pro - Aadhaar Entry")
        self.setGeometry(100, 100, 800, 600)
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
            QMessageBox.information(self, "Success", "Aadhaar and Voter ID Validated. Proceeding to Biometric Capture.")
            self.stacked_widget.setCurrentIndex(1)  # Switch to Biometric Capture Screen
        else:
            QMessageBox.warning(self, "Error", "Invalid Aadhaar Number or Voter ID. Please enter valid details.")

if __name__ == "__main__":
    app = QApplication([])
    window = AadhaarEntryScreen()
    window.show()
    app.exec_()
