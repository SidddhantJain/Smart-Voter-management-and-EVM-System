# Models for Camera Analytics

Place model files here to enable high-fidelity, model-driven overlays.

## Emotion (FER+ ONNX)
- File: `ferplus.onnx`
- Source: https://github.com/onnx/models/raw/main/vision/body_analysis/emotion_ferplus/model/emotion-ferplus-8.onnx

The application will auto-download this file if missing, but placing it here avoids first-run latency.

## Age/Gender (Caffe)
Place the following files:
- `deploy_age.prototxt`
- `age_net.caffemodel`
- `deploy_gender.prototxt`
- `gender_net.caffemodel`

Source: https://github.com/spmallick/learnopencv/tree/master/AgeGender/models

## Notes
- Global overlays toggle: set `VOTEGUARD_OVERLAYS=0` to disable text/box overlays across demos and UI components.
- Default model directory is resolved to this folder if present.
- If models are not present, the system falls back gracefully or logs minimal information.
