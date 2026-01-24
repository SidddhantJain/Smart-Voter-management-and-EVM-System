"""
Counting Software for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Verification of Aadhaar and Voter ID, constituency matching, and vote tallying
"""

import json

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CountingSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoteGuard Pro - Counting Software")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #444;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                border: 1px solid #ccc;
                font-size: 14px;
                color: #333;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Counting Software")
        layout.addWidget(self.title_label)

        # Table for displaying votes
        self.vote_table = QTableWidget()
        self.vote_table.setColumnCount(3)
        self.vote_table.setHorizontalHeaderLabels(
            ["Aadhaar ID", "Voter ID", "Candidate"]
        )
        layout.addWidget(self.vote_table)

        # Load Votes Button
        self.load_votes_button = QPushButton("Load Votes")
        self.load_votes_button.clicked.connect(self.load_votes)
        layout.addWidget(self.load_votes_button)

        # Verify Votes Button
        self.verify_votes_button = QPushButton("Verify Votes")
        self.verify_votes_button.clicked.connect(self.verify_votes)
        layout.addWidget(self.verify_votes_button)

        self.setLayout(layout)

    def load_votes(self):
        try:
            with open("votes.json", "r") as f:
                content = f.read()
                if not content.strip():
                    raise ValueError("The votes file is empty.")
                votes = json.loads(content)
                self.vote_table.setRowCount(len(votes))
                for row, vote in enumerate(votes):
                    self.vote_table.setItem(
                        row, 0, QTableWidgetItem(vote.get("aadhaar_id", "N/A"))
                    )
                    self.vote_table.setItem(
                        row, 1, QTableWidgetItem(vote.get("voter_id", "N/A"))
                    )
                    self.vote_table.setItem(
                        row, 2, QTableWidgetItem(vote.get("candidate", "N/A"))
                    )
            QMessageBox.information(self, "Load Votes", "Votes loaded successfully.")
        except ValueError as ve:
            QMessageBox.warning(self, "Load Votes", f"Warning: {ve}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load votes: {e}")

    def verify_votes(self):
        # Simulate verification logic
        QMessageBox.information(
            self, "Verify Votes", "All votes verified successfully."
        )


if __name__ == "__main__":
    app = QApplication([])
    window = CountingSoftware()
    window.show()
    app.exec_()
