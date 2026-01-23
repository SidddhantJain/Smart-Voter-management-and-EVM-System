import argparse
import json
from pathlib import Path
from voteguard.config.env import data_dir, key_path
from voteguard.core.counting import tally


def main():
    parser = argparse.ArgumentParser(description="Tally votes from ballot ledger")
    parser.add_argument("--ledger", type=str, default=str(data_dir() / "ballot_ledger.json"), help="Path to ballot ledger JSON")
    parser.add_argument("--key", type=str, default=str(key_path()), help="Path to Fernet key file")
    parser.add_argument("--out", type=str, default="", help="Optional path to write tally JSON")
    parser.add_argument("--no-verify", action="store_true", help="Skip ledger integrity verification")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    key = Path(args.key)
    counts = tally(ledger_path, key, verify=not args.no_verify)

    print("Vote Tally:")
    for election, choices in counts.items():
        print(f"- {election}")
        for choice, c in sorted(choices.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  * {choice}: {c}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(counts, indent=2))
        print(f"\nSaved tally to {out_path}")


if __name__ == "__main__":
    main()
