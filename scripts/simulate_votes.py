import os
import argparse
from voteguard.app import bootstrap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=3, help="Number of votes to simulate")
    parser.add_argument("--reset", action="store_true", help="Reset ledgers and cast registry before simulating")
    args = parser.parse_args()

    os.environ.setdefault("VOTEGUARD_DATA", "./data")
    os.environ.setdefault("VOTEGUARD_ASSURANCE", "L0")
    data_dir = os.getenv("VOTEGUARD_DATA", "./data")
    os.makedirs(data_dir, exist_ok=True)

    if args.reset:
        for name in ("ballot_ledger.json", "audit_ledger.json", "cast_registry.json", os.path.basename(os.getenv("FERNET_KEY_PATH", "key.key"))):
            path = os.path.join(data_dir, name)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    cv = bootstrap()
    for i in range(1, args.n + 1):
        try:
            # Unique ids per run using index + process id
            aadhaar = f"{os.getpid()%9999:04d}{i:08d}"
            voter = f"VG{i:06d}{os.getpid()%1000:03d}"
            r = cv.execute("GENERAL", f"Party-{i%3}", aadhaar=aadhaar, voter_id=voter)
            print(f"Vote {i}: seq={r.seq} receipt={r.receipt_id[:12]}…")
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
