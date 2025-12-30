import os
from voteguard.app import bootstrap


def main(n: int = 3):
    os.environ.setdefault("VOTEGUARD_DATA", "./data")
    os.environ.setdefault("VOTEGUARD_ASSURANCE", "L0")
    cv = bootstrap()
    for i in range(1, n + 1):
        try:
            r = cv.execute("GENERAL", f"Party-{i%3}", aadhaar=f"9999{i:08d}", voter_id=f"VOTE{i:06d}")
            print(f"Vote {i}: seq={r.seq} receipt={r.receipt_id[:12]}…")
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
