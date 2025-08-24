"""
Anomaly Detection Calibration
Language: Python
Handles: Fine-tuning thresholds for anomaly detection
"""
import numpy as np

class AnomalyDetection:
    def __init__(self):
        self.threshold = 0.5  # Default threshold

    def calibrate_threshold(self, data):
        """
        Calibrate the anomaly detection threshold based on data.
        :param data: List of anomaly scores.
        """
        self.threshold = np.percentile(data, 95)  # Set threshold to 95th percentile
        print(f"[Anomaly Detection] Threshold calibrated to: {self.threshold}")

    def detect_anomalies(self, data):
        """
        Detect anomalies based on the calibrated threshold.
        :param data: List of anomaly scores.
        :return: List of detected anomalies.
        """
        anomalies = [score for score in data if score > self.threshold]
        print(f"[Anomaly Detection] Detected anomalies: {anomalies}")
        return anomalies

if __name__ == "__main__":
    ad = AnomalyDetection()
    sample_data = np.random.rand(100)
    ad.calibrate_threshold(sample_data)
    ad.detect_anomalies(sample_data)
