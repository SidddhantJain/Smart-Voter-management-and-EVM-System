"""
Pattern Recognition for Voting Data
Language: Python
Handles: Detecting irregular patterns in voting data
"""
import numpy as np
import pandas as pd

class PatternRecognition:
    def __init__(self):
        pass

    def detect_irregularities(self, data_path):
        """
        Detect irregular patterns in voting data.
        :param data_path: Path to the dataset.
        :return: List of irregularities detected.
        """
        data = pd.read_csv(data_path)
        irregularities = []

        # Example: Check for duplicate voter IDs
        if data["voter_id"].duplicated().any():
            irregularities.append("Duplicate voter IDs detected.")

        # Example: Check for votes cast outside registered constituency
        if (data["casted_constituency"] != data["registered_constituency"]).any():
            irregularities.append("Votes cast outside registered constituency detected.")

        return irregularities

if __name__ == "__main__":
    pr = PatternRecognition()
    irregularities = pr.detect_irregularities("voting_data.csv")
    print("Irregularities Detected:", irregularities)
