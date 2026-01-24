"""
Machine Learning Model Training for Fraud Detection
Language: Python
Handles: Data preprocessing, model training, and evaluation
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


class FraudDetectionModel:
    def __init__(self):
        self.model = RandomForestClassifier()

    def preprocess_data(self, data_path):
        """
        Load and preprocess data for training.
        :param data_path: Path to the dataset.
        :return: Preprocessed features and labels.
        """
        data = pd.read_csv(data_path)
        X = data.drop("label", axis=1)
        y = data["label"]
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train, y_train):
        """
        Train the fraud detection model.
        :param X_train: Training features.
        :param y_train: Training labels.
        """
        self.model.fit(X_train, y_train)
        print("[ML] Model training completed.")

    def evaluate_model(self, X_test, y_test):
        """
        Evaluate the trained model.
        :param X_test: Test features.
        :param y_test: Test labels.
        """
        predictions = self.model.predict(X_test)
        report = classification_report(y_test, predictions)
        print("[ML] Model Evaluation Report:\n", report)


if __name__ == "__main__":
    model = FraudDetectionModel()
    X_train, X_test, y_train, y_test = model.preprocess_data("fraud_data.csv")
    model.train_model(X_train, y_train)
    model.evaluate_model(X_test, y_test)
