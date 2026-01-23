import sys
from pathlib import Path

# Ensure workspace root is on sys.path for package imports
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from voteguard.config.env import data_dir, key_path
from voteguard.core.counting import tally


def main() -> int:
    ledger = data_dir() / "ballot_ledger.json"
    key = key_path()
    try:
        counts = tally(ledger, key, verify=True)
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    print("Vote Tally:")
    for election, choices in counts.items():
        print(f"- {election}")
        for choice, c in sorted(choices.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  * {choice}: {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
