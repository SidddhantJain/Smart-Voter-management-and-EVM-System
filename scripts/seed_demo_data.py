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


def main() -> None:
    random.seed(42)
    init_db()

    constituencies = []
    with SessionLocal() as db:
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

            node = db.get(GraphNode, voter_id)
            if node is None:
                db.add(GraphNode(id=voter_id, label=voter_id, kind="voter"))

        for constituency_id in constituencies:
            node = db.get(GraphNode, constituency_id)
            if node is None:
                db.add(GraphNode(id=constituency_id, label=constituency_id.replace("CONS-", "Ward "), kind="constituency"))

        db.commit()

        existing_edges = {(edge.source, edge.target, edge.relation) for edge in db.query(GraphEdge).all()}
        for index in range(1, 61):
            voter_id = f"VG-{index:04d}"
            constituency_id = constituencies[(index - 1) % len(constituencies)]
            key = (voter_id, constituency_id, "assigned_to")
            if key not in existing_edges:
                db.add(GraphEdge(source=voter_id, target=constituency_id, relation="assigned_to"))

        db.commit()

    print("Seeded 60 voters, 10 constituencies, and graph edges.")


if __name__ == "__main__":
    main()