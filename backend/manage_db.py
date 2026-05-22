from __future__ import annotations

import argparse
from pathlib import Path
import sys

from alembic import command
from alembic.config import Config


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def get_alembic_config() -> Config:
    config = Config(str(REPO_ROOT / "backend" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "backend" / "migrations"))
    return config


def upgrade() -> None:
    command.upgrade(get_alembic_config(), "head")


def downgrade_base() -> None:
    command.downgrade(get_alembic_config(), "base")


def reset() -> None:
    downgrade_base()
    upgrade()


def current() -> None:
    command.current(get_alembic_config(), verbose=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="VoteGuard Nexus database helper")
    parser.add_argument(
        "command",
        choices=("upgrade", "downgrade", "reset", "current"),
        help="Database command to run",
    )
    args = parser.parse_args()

    if args.command == "upgrade":
        upgrade()
    elif args.command == "downgrade":
        downgrade_base()
    elif args.command == "reset":
        reset()
    elif args.command == "current":
        current()


if __name__ == "__main__":
    main()
