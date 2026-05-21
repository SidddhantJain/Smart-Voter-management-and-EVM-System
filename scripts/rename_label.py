"""
Rename a label directory under `imd/` (e.g., rename `siddhant` to `siddhat`) and update any label map if present.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional


def rename_label(old: str, new: str, imd_dir: str = "imd") -> None:
    base = Path(imd_dir)
    old_dir = base / old
    new_dir = base / new
    if not old_dir.exists():
        raise RuntimeError(f"Source label directory not found: {old_dir}")
    if new_dir.exists():
        raise RuntimeError(f"Destination label directory already exists: {new_dir}")
    shutil.move(str(old_dir), str(new_dir))
    # update labels.json if exists in voteguard/demo/models
    labels_path = Path("voteguard") / "demo" / "models" / "labels.json"
    if labels_path.exists():
        with labels_path.open("r", encoding="utf-8") as f:
            labels = json.load(f)
        changed = False
        for k, v in list(labels.items()):
            if v == old:
                labels[k] = new
                changed = True
        if changed:
            with labels_path.open("w", encoding="utf-8") as f:
                json.dump(labels, f, indent=2)
            print(f"Updated label map at {labels_path}")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--imd", default="imd")
    args = p.parse_args()
    rename_label(args.old, args.new, imd_dir=args.imd)
    print(f"Renamed {args.old} -> {args.new} in {args.imd}")
