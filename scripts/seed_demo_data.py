from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.db import SessionLocal, init_db  # noqa: E402
from backend.core.models import Constituency, GraphEdge, GraphNode, Voter  # noqa: E402


FIRST_NAMES = [
    "Aarav", "Isha", "Rohan", "Meera", "Kabir", "Diya", "Ayaan", "Ananya", "Vihaan", "Priya",
    "Arjun", "Sara", "Reyansh", "Nina", "Advait", "Kavya", "Yash", "Riya", "Dev", "Sana",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Gupta", "Singh", "Khan", "Jain", "Mehta", "Reddy", "Nair",
    "Das", "Chopra", "Bose", "Kapoor", "Malhotra", "Joshi", "Pillai", "Ahuja", "Sethi", "Iyer",
]
STATES = ["Maharashtra", "Karnataka", "Tamil Nadu", "Gujarat", "Punjab", "Kerala"]
DISTRICTS = ["North", "South", "East", "West", "Central", "Urban"]

GRAPH_CENTRAL_ID = "CENTRAL-ECI"
STATE_IDS = [f"STATE-{name.upper().replace(' ', '-') }" for name in STATES[:5]]


def main() -> None:
    random.seed(42)
    init_db()

    with SessionLocal() as db:
        db.query(GraphEdge).delete()
        db.query(GraphNode).delete()

        constituencies = []
        for index in range(1, 11):
            constituency_id = f"CONS-{index:03d}"
            constituency = db.get(Constituency, constituency_id)
            if constituency is None:
                constituency = Constituency(
                    constituency_id=constituency_id,
                    name=f"Constituency {index}",
                    state=random.choice(STATES),
                    district=random.choice(DISTRICTS),
                )
                db.add(constituency)
            constituencies.append(constituency_id)

        for index in range(1, 61):
            voter_id = f"VG-{index:04d}"
            voter = db.get(Voter, voter_id)
            if voter is None:
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                constituency = random.choice(constituencies)
                db.add(Voter(voter_id=voter_id, first_name=first_name, last_name=last_name, constituency=constituency))

        # Layer 1: central authority
        db.add(GraphNode(id=GRAPH_CENTRAL_ID, label="Central Election Commission", kind="central"))

        # Layer 2: state branches
        for state_id, state_name in zip(STATE_IDS, STATES[:5]):
            db.add(GraphNode(id=state_id, label=state_name, kind="state"))
            db.add(GraphEdge(source=GRAPH_CENTRAL_ID, target=state_id, relation="reports_to"))

        # Layer 3: local constituencies, two per state
        constituency_state_pairs = []
        for index, constituency_id in enumerate(constituencies):
            state_id = STATE_IDS[index // 2]
            constituency_state_pairs.append((constituency_id, state_id))
            db.add(GraphNode(id=constituency_id, label=f"Ward {index + 1:02d}", kind="local"))
            db.add(GraphEdge(source=state_id, target=constituency_id, relation="oversees"))

        # Layer 4: voter leaves, 54 visible in graph for a 70-node / 60-edge demo.
        linked_voters = 45
        for index in range(1, 55):
            voter_id = f"VG-{index:04d}"
            node = db.get(GraphNode, voter_id)
            if node is None:
                db.add(GraphNode(id=voter_id, label=voter_id, kind="voter"))
            if index <= linked_voters:
                constituency_id = constituency_state_pairs[(index - 1) % len(constituency_state_pairs)][0]
                db.add(GraphEdge(source=constituency_id, target=voter_id, relation="assigned_to"))

        db.commit()

    print("Seeded a layered graph with 70 nodes and 60 edges.")


if __name__ == "__main__":
    main()