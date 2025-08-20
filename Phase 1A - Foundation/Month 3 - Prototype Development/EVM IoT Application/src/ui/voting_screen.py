"""
Voting Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Displaying parties, election type, and casting votes
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from backend.vote_storage import VoteStorage

class VotingScreen(QWidget):
    def __init__(self, election_type, parties):
        super().__init__()
        self.setWindowTitle("VoteGuard Pro - Voting Screen")
        self.setGeometry(100, 100, 800, 600)
        self.election_type = election_type
        self.parties = parties
        self.vote_storage = VoteStorage()  # Initialize backend
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Election Type Display
        self.election_label = QLabel(f"Election Type: {self.election_type}")
        layout.addWidget(self.election_label)

        # Timer for Continuous Display
        self.timer_label = QLabel()
        layout.addWidget(self.timer_label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Party Buttons
        for party in self.parties:
            party_layout = QHBoxLayout()

            # Party Details
            party_label = QLabel(f"{party['name']} ({party['symbol']})")
            party_layout.addWidget(party_label)

            # Vote Button
            vote_button = QPushButton(f"Vote for {party['name']}")
            vote_button.clicked.connect(lambda _, p=party: self.cast_vote(p))
            party_layout.addWidget(vote_button)

            layout.addLayout(party_layout)

        self.setLayout(layout)

    def update_time(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.timer_label.setText(f"Current Time: {current_time}")

    def cast_vote(self, party):
        print(f"[VOTE] Cast vote for {party['name']} ({party['symbol']})")
        self.vote_storage.store_vote(self.election_type, party['name'])
        QMessageBox.information(self, "Vote Cast", f"Your vote for {party['name']} has been recorded.")

        # Reset UI for next voter
        self.reset_ui()

    def reset_ui(self):
        # Clear any dynamic elements and reset the screen for the next voter
        self.timer_label.setText("")
        self.timer.start(1000)  # Restart the timer
        QMessageBox.information(self, "Next Voter", "Please prepare for the next voter.")

if __name__ == "__main__":
    app = QApplication([])
    parties = [
        {"name": "Party A", "symbol": "Symbol A"},
        {"name": "Party B", "symbol": "Symbol B"},
        {"name": "Party C", "symbol": "Symbol C"},
        {"name": "Party D", "symbol": "Symbol D"},
        {"name": "Party E", "symbol": "Symbol E"},
    ]
    window = VotingScreen("State Assembly", parties)
    window.show()
    app.exec_()
