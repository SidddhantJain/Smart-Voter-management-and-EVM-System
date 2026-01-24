"""
ArcFace Implementation for Face Recognition
Language: Python
Handles: Highly accurate face recognition using ArcFace
"""

import cv2
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import normalize


class ArcFaceRecognition:
    def __init__(self, model_path):
        """
        Initialize the ArcFace model.
        :param model_path: Path to the pre-trained ArcFace model.
        """
        self.model = tf.keras.models.load_model(model_path)

    def preprocess_image(self, image_path):
        """
        Preprocess the input image for ArcFace.
        :param image_path: Path to the image file.
        :return: Preprocessed image.
        """
        image = cv2.imread(image_path)
        image = cv2.resize(image, (112, 112))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.transpose(image, (2, 0, 1))  # HWC to CHW
        image = normalize(image, axis=1)
        return np.expand_dims(image, axis=0)

    def get_embedding(self, image_path):
        """
        Generate the face embedding for the given image.
        :param image_path: Path to the image file.
        :return: Face embedding vector.
        """
        preprocessed_image = self.preprocess_image(image_path)
        embedding = self.model.predict(preprocessed_image)
        return embedding

    def compare_faces(self, embedding1, embedding2, threshold=0.6):
        """
        Compare two face embeddings.
        :param embedding1: First face embedding.
        :param embedding2: Second face embedding.
        :param threshold: Similarity threshold.
        :return: Boolean indicating if the faces match.
        """
        distance = np.linalg.norm(embedding1 - embedding2)
        return distance < threshold


if __name__ == "__main__":
    arcface = ArcFaceRecognition("arcface_model.h5")
    embedding1 = arcface.get_embedding("face1.jpg")
    embedding2 = arcface.get_embedding("face2.jpg")
    match = arcface.compare_faces(embedding1, embedding2)
    print(f"Faces Match: {match}")
