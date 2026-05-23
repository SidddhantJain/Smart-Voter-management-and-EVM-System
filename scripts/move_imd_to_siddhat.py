"""Move JPG images from `imd/` root into `imd/siddhat/` for training.
"""
from pathlib import Path
import shutil


def main():
    src = Path("imd")
    dst = src / "siddhat"
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for p in sorted(src.glob("*.jpg")):
        try:
            shutil.move(str(p), str(dst / p.name))
            count += 1
        except Exception:
            continue
    print("moved", count)


if __name__ == "__main__":
    main()
