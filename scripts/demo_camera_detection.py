import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

# Resolve repo root and add EVM src to path
repo_root = Path(__file__).resolve().parents[1]
src_dir = (
    repo_root
    / "Phase 1A - Foundation"
    / "Month 3 - Prototype Development"
    / "EVM IoT Application"
    / "src"
)
sys.path.append(str(src_dir))

import os

from ml.demographics_recognizer import DemographicsRecognizer
from ml.emotion_recognizer import EmotionRecognizer


def _try_open_camera() -> cv2.VideoCapture:
    """Try multiple backends and indices to open a camera reliably on Windows."""
    indices = [0, 1, 2, 3]
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    for backend in backends:
        for idx in indices:
            cap = cv2.VideoCapture(idx, backend)
            if cap.isOpened():
                return cap
            cap.release()
    # Fallback
    return cv2.VideoCapture(0)


def _age_bucket_for_value(age: int) -> str:
    """Map numeric age to the closest bucket label."""
    buckets = [
        (0, 2, "(0-2)"),
        (4, 6, "(4-6)"),
        (8, 12, "(8-12)"),
        (15, 20, "(15-20)"),
        (25, 32, "(25-32)"),
        (38, 43, "(38-43)"),
        (48, 53, "(48-53)"),
        (60, 100, "(60-100)"),
    ]
    for lo, hi, label in buckets:
        if lo <= age <= hi:
            return label
    # nearest fallback
    return "(25-32)" if 22 <= age <= 35 else "(60-100)" if age >= 60 else "(15-20)"


def main():
    parser = argparse.ArgumentParser(
        description="Camera detection demo with emotion and demographics overlays (model-driven)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without GUI; save annotated frames to --save-dir",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default=str(repo_root / "output" / "camera_headless"),
        help="Directory to save frames in headless mode",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=-1,
        help="Number of frames to process in headless mode (-1 for infinite)",
    )
    args = parser.parse_args()

    print("[Demo] Starting camera detection demo… Press 'q' to quit.")
    overlays_on = os.getenv("VOTEGUARD_OVERLAYS", "1") == "1"

    # Initialize recognizers (will auto-download age/gender models if missing)
    emo = EmotionRecognizer()
    demo = DemographicsRecognizer()

    # Face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    cap = _try_open_camera()
    if not cap.isOpened():
        print("[Error] Could not open camera.")
        return

    if args.headless:
        save_dir = Path(args.save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f"[Headless] Saving frames to: {save_dir}")

    last_log = 0.0
    processed = 0
    try:
        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                print("[Warn] Frame grab failed; retrying…")
                time.sleep(0.05)
                continue

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80)
            )

            for x, y, w, h in faces:
                roi_rgb = frame_rgb[y : y + h, x : x + w]
                # Predict emotion and demographics (model-driven only)
                label, conf = emo.predict(roi_rgb)
                age_bucket, age_conf, gender_label, gender_conf = demo.predict(roi_rgb)

                # Draw overlays if enabled
                if overlays_on:
                    cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    text = f"{gender_label} ({gender_conf:.2f}) | {age_bucket} ({age_conf:.2f}) | {label} ({conf:.2f})"
                    y_text = y - 10 if y - 10 > 20 else y + 25
                    cv2.putText(
                        frame_bgr,
                        text,
                        (x, y_text),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (50, 200, 255),
                        2,
                        cv2.LINE_AA,
                    )

            # Periodic console log
            now = time.time()
            if overlays_on and now - last_log > 2.0 and len(faces) > 0:
                x, y, w, h = faces[0]
                roi_rgb = frame_rgb[y : y + h, x : x + w]
                label, conf = emo.predict(roi_rgb)
                age_bucket, age_conf, gender_label, gender_conf = demo.predict(roi_rgb)
                print(
                    f"[Info] Face -> Gender: {gender_label} ({gender_conf:.2f}), Age: {age_bucket} ({age_conf:.2f}), Emotion: {label} ({conf:.2f})"
                )
                last_log = now

            if args.headless:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                out_path = Path(args.save_dir) / f"frame_{ts}.jpg"
                cv2.imwrite(str(out_path), frame_bgr)
                processed += 1
                if args.frames > 0 and processed >= args.frames:
                    print(f"[Headless] Processed {processed} frames; exiting.")
                    break
                # Small sleep to avoid spamming disk too fast
                time.sleep(0.02)
            else:
                cv2.imshow("Camera Detection Demo", frame_bgr)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

    except KeyboardInterrupt:
        print("\n[Demo] Interrupted by user; closing…")
    finally:
        cap.release()
        if not args.headless:
            cv2.destroyAllWindows()
        print("[Demo] Camera demo closed.")


if __name__ == "__main__":
    main()
