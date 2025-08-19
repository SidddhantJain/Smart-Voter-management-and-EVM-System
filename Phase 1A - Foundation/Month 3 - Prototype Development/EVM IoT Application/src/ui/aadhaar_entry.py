"""
Aadhaar Entry Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Aadhaar number input, biometric capture initiation
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class AadhaarEntryScreen(QWidget):
    def __init__(self):
        super().__init__()
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

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.validate_aadhaar)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def validate_aadhaar(self):
        aadhaar_number = self.aadhaar_input.text()
        if len(aadhaar_number) == 12 and aadhaar_number.isdigit():
            QMessageBox.information(self, "Success", "Aadhaar Number Validated. Proceeding to Biometric Capture.")
            # TODO: Transition to biometric capture screen
        else:
            QMessageBox.warning(self, "Error", "Invalid Aadhaar Number. Please enter a valid 12-digit number.")

if __name__ == "__main__":
    app = QApplication([])
    window = AadhaarEntryScreen()
    window.show()
    app.exec_()
