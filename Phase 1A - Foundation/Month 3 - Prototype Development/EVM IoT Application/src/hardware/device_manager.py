"""
Device Manager for VoteGuard Pro EVM
Language: Python
Handles: Initialization and management of all hardware peripherals
"""

from .biometric import Camera, FingerprintSensor, RetinaScanner


class DeviceManager:
    def __init__(self):
        self.fingerprint = FingerprintSensor()
        self.retina = RetinaScanner()
        self.camera = Camera()

    def initialize_all(self):
        print("[HW] Initializing fingerprint, retina, and camera devices...")
        return {
            "fingerprint": self.fingerprint.initialize(),
            "retina": self.retina.initialize(),
            "camera": self.camera.initialize(),
        }

    def capture_all(self):
        print("[HW] Capturing from fingerprint, retina, and camera devices...")
        return {
            "fingerprint": self.fingerprint.capture(),
            "retina": self.retina.capture(),
            "camera": self.camera.capture(),
        }
