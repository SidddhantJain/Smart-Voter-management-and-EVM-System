"""
Voting Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Displaying parties, election type, and casting votes
"""
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QTimer
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))
from backend.vote_storage import VoteStorage
from ui.vote_visualizer import visualize_vote
from backend.cast_registry import has_cast, mark_cast
from PyQt5.QtGui import QPixmap

class VotingScreen(QWidget):
    def __init__(self, election_type, parties, aadhaar_id=None, voter_id=None):
        super().__init__()
        self.setWindowTitle("VoteGuard Pro - Voting Screen")
        self.setGeometry(100, 100, 800, 600)
        self.election_type = election_type
        self.parties = parties
        self.aadhaar_id = aadhaar_id
        self.voter_id = voter_id
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

        # Placeholder image (captured face)
        placeholder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'captured_face.jpg'))
        if os.path.exists(placeholder_path):
            img_label = QLabel()
            pix = QPixmap(placeholder_path)
            if not pix.isNull():
                img_label.setPixmap(pix.scaled(160, 160))
                layout.addWidget(img_label)

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
        # Prevent double voting by Aadhaar/Voter ID
        if self.aadhaar_id and self.voter_id and has_cast(self.aadhaar_id, self.voter_id):
            QMessageBox.warning(self, "Already Voted", "This Aadhaar/Voter ID has already voted.")
            return
        print(f"[VOTE] Cast vote for {party['name']} ({party['symbol']})")
        self.vote_storage.store_vote(self.election_type, party['name'])
        # Mark as cast
        if self.aadhaar_id and self.voter_id:
            mark_cast(self.aadhaar_id, self.voter_id)
        QMessageBox.information(self, "Vote Cast", f"Your vote for {party['name']} has been recorded.")

        # Visualization: show candidate card → ballot box → blockchain
        image_path = self._resolve_candidate_image(party)
        visualize_vote(self, party['name'], image_path)

        # Transition back to Aadhaar Entry UI
        self.transition_to_aadhaar_entry()

    def transition_to_aadhaar_entry(self):
        # Emit a signal or directly transition to Aadhaar Entry UI
        QMessageBox.information(self, "Next Voter", "Returning to Aadhaar Entry for the next voter.")
        self.parentWidget().setCurrentIndex(0)  # Assuming Aadhaar Entry is at index 0

    def _resolve_candidate_image(self, party):
        """Try to find a candidate image in assets; return None if not found."""
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        # Common locations
        candidates_dir = os.path.join(base, 'assets', 'candidates')
        possible = [
            os.path.join(candidates_dir, f"{party['name']}.png"),
            os.path.join(candidates_dir, f"{party['name']}.jpg"),
            os.path.join(candidates_dir, f"{party['symbol']}.png"),
            os.path.join(candidates_dir, f"{party['symbol']}.jpg"),
        ]
        for p in possible:
            if os.path.exists(p):
                return p
        return None

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
