import sys
import time
from pathlib import Path

import cv2

# Resolve repo root and add EVM src to path
repo_root = Path(__file__).resolve().parents[1]
src_dir = repo_root / "Phase 1A - Foundation" / "Month 3 - Prototype Development" / "EVM IoT Application" / "src"
sys.path.append(str(src_dir))

from ml.emotion_recognizer import EmotionRecognizer
from ml.demographics_recognizer import DemographicsRecognizer


def main():
    print("[Demo] Starting camera detection demo… Press 'q' to quit.")

    # Initialize recognizers (will auto-download age/gender models if missing)
    emo = EmotionRecognizer()
    demo = DemographicsRecognizer()

    # Face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Error] Could not open camera.")
        return

    last_log = 0.0
    try:
        while True:
            ret, frame_bgr = cap.read()
            if not ret:
                print("[Warn] Frame grab failed; retrying…")
                time.sleep(0.05)
                continue

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80))

            for (x, y, w, h) in faces:
                roi_rgb = frame_rgb[y:y+h, x:x+w]
                # Predict emotion and demographics
                label, conf = emo.predict(roi_rgb)
                age_bucket, age_conf, gender_label, gender_conf = demo.predict(roi_rgb)

                # Draw overlays
                cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), (0, 255, 0), 2)
                text = f"{gender_label} ({gender_conf:.2f}) | {age_bucket} ({age_conf:.2f}) | {label} ({conf:.2f})"
                y_text = y - 10 if y - 10 > 20 else y + 25
                cv2.putText(frame_bgr, text, (x, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 200, 255), 2, cv2.LINE_AA)

            # Periodic console log
            now = time.time()
            if now - last_log > 2.0 and len(faces) > 0:
                # log first face
                (x, y, w, h) = faces[0]
                roi_rgb = frame_rgb[y:y+h, x:x+w]
                label, conf = emo.predict(roi_rgb)
                age_bucket, age_conf, gender_label, gender_conf = demo.predict(roi_rgb)
                print(f"[Info] Face -> Gender: {gender_label} ({gender_conf:.2f}), Age: {age_bucket} ({age_conf:.2f}), Emotion: {label} ({conf:.2f})")
                last_log = now

            cv2.imshow('Camera Detection Demo', frame_bgr)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[Demo] Interrupted by user; closing…")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[Demo] Camera demo closed.")


if __name__ == '__main__':
    main()
