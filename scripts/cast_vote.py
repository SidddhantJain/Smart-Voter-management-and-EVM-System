import argparse
from voteguard.app import bootstrap


def main():
    parser = argparse.ArgumentParser(description="Cast a vote into the encrypted ledger")
    parser.add_argument("--election", required=True, help="Election type (e.g., GENERAL)")
    parser.add_argument("--choice", required=True, help="Candidate/party identifier (non-PII)")
    parser.add_argument("--aadhaar", required=True, help="Voter Aadhaar number (for hash only)")
    parser.add_argument("--voter-id", required=True, help="Voter ID (for hash only)")
    args = parser.parse_args()

    cv = bootstrap()
    receipt = cv.execute(args.election, args.choice, aadhaar=args.aadhaar, voter_id=args.voter_id)
    print("Vote stored.")
    print(f" - seq: {receipt.seq}")
    print(f" - receipt_id: {receipt.receipt_id}")


if __name__ == "__main__":
    main()
