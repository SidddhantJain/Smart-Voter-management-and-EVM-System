"""
Voting Screen for VoteGuard Pro EVM
Language: Python (PyQt5)
Handles: Displaying parties, election type, and casting votes
"""

import datetime
import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
)
from PyQt5.QtGui import QPixmap
from ui.vote_visualizer import visualize_vote

from voteguard.adapters.audit_helper import SafeAuditLogger
from voteguard.app import bootstrap
from voteguard.core.state_machine import State


class VotingScreen(QWidget):
    def __init__(
        self, election_type, parties, aadhaar_id=None, voter_id=None, session_id=None
    ):
        super().__init__()
        self.setWindowTitle("VoteGuard Pro - Voting Screen")
        self.setGeometry(100, 100, 800, 600)
        self.election_type = election_type
        self.parties = parties
        self.aadhaar_id = aadhaar_id
        self.voter_id = voter_id
        self.session_id = session_id
        # Core casting service (simulation-first, PII-safe)
        self.cast_service = bootstrap()
        self.audit = SafeAuditLogger()
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
        placeholder_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "captured_face.jpg"
            )
        )
        if os.path.exists(placeholder_path):
            img_label = QLabel()
            pix = QPixmap(placeholder_path)
            if not pix.isNull():
                img_label.setPixmap(pix.scaled(160, 160))
                layout.addWidget(img_label)

        # Party Buttons with logos and candidate images
        for party in self.parties:
            party_layout = QHBoxLayout()

            # Logo (if provided)
            logo_path = party.get("logo_path") or ""
            if logo_path and os.path.exists(logo_path):
                logo_lbl = QLabel()
                logo_pix = QPixmap(logo_path)
                if not logo_pix.isNull():
                    logo_lbl.setPixmap(logo_pix.scaled(48, 48))
                    party_layout.addWidget(logo_lbl)

            # Candidate image (if provided)
            image_path = party.get("image_path") or self._resolve_candidate_image(party)
            if image_path and os.path.exists(image_path):
                img_lbl = QLabel()
                img_pix = QPixmap(image_path)
                if not img_pix.isNull():
                    img_lbl.setPixmap(img_pix.scaled(64, 64))
                    party_layout.addWidget(img_lbl)

            # Party and candidate details
            candidate_name = party.get("candidate_name") or party.get("candidate") or ""
            party_label = QLabel(
                f"{party['name']} ({party.get('symbol','')})"
                + (f" — {candidate_name}" if candidate_name else "")
            )
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
        try:
            print(f"[VOTE] Cast vote for {party['name']} ({party['symbol']})")
            self.audit.log(
                "VOTE_ATTEMPT",
                {
                    "session_id": getattr(
                        self.parentWidget(), "session_id", self.session_id
                    ),
                    "election_type": self.election_type,
                },
            )
            # State to SECURE_STORAGE (conceptual step)
            if hasattr(self.parentWidget(), "set_state"):
                self.parentWidget().set_state(State.SECURE_STORAGE)
            receipt = self.cast_service.execute(
                election=self.election_type,
                choice=party["name"],
                aadhaar=self.aadhaar_id or "",
                voter_id=self.voter_id or "",
            )
        except ValueError:
            QMessageBox.warning(
                self, "Already Voted", "This Aadhaar/Voter ID has already voted."
            )
            return
        except Exception as e:
            QMessageBox.critical(self, "Storage Error", f"Failed to store vote: {e}")
            return

        # Visualization: show candidate card → ballot box → blockchain
        image_path = party.get("image_path") or self._resolve_candidate_image(party)

        def after_visual():
            # Only after visualization completes, show confirmation and return
            QMessageBox.information(
                self,
                "Vote Cast",
                f"Your vote for {party['name']} has been recorded.\nReceipt: {receipt.receipt_id}",
            )
            self.audit.log(
                "VOTE_STORED",
                {
                    "session_id": getattr(
                        self.parentWidget(), "session_id", self.session_id
                    ),
                    "election_type": self.election_type,
                    "receipt_id": receipt.receipt_id,
                },
            )
            # Move to RECEIPT state
            if hasattr(self.parentWidget(), "set_state"):
                self.parentWidget().set_state(State.RECEIPT)
            # Small delay before returning to Aadhaar Entry
            from PyQt5.QtCore import QTimer

            QTimer.singleShot(600, self.transition_to_aadhaar_entry)

        visualize_vote(self, party["name"], image_path, on_done=after_visual)

    def transition_to_aadhaar_entry(self):
        # Emit a signal or directly transition to Aadhaar Entry UI
        self.audit.log(
            "SESSION_RESET",
            {"session_id": getattr(self.parentWidget(), "session_id", self.session_id)},
        )
        QMessageBox.information(
            self, "Next Voter", "Returning to Aadhaar Entry for the next voter."
        )
        # State: RECEIPT -> RESET -> AADHAAR_ENTRY
        parent = self.parentWidget()
        try:
            if hasattr(parent, "set_state"):
                parent.set_state(State.RESET)
            if hasattr(parent, "navigate_to"):
                parent.navigate_to(0, State.AADHAAR_ENTRY)
            else:
                parent.setCurrentIndex(0)
            # Clear session id on reset
            if hasattr(parent, "session_id"):
                parent.session_id = None
        except Exception:
            parent.setCurrentIndex(0)

    def _resolve_candidate_image(self, party):
        """Try to find a candidate image in assets; return None if not found."""
        base = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        # Common locations
        candidates_dir = os.path.join(base, "assets", "candidates")
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
