"""
Python interface for biometric and camera C++ drivers (fingerprint, retina, camera)
Uses ctypes or cffi to call C++ shared libraries
"""

import ctypes
import os

# Load shared libraries (assume .dll/.so/.dylib built from C++ code)
LIB_PATH = os.path.dirname(__file__)


class FingerprintSensor:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(LIB_PATH, "fingerprint_sensor.so"))
        self.lib.initialize.restype = ctypes.c_bool
        self.lib.captureFingerprint.restype = ctypes.c_bool

    def initialize(self):
        return self.lib.initialize()

    def capture(self):
        return self.lib.captureFingerprint()


class RetinaScanner:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(LIB_PATH, "retina_scanner.so"))
        self.lib.initialize.restype = ctypes.c_bool
        self.lib.captureRetina.restype = ctypes.c_bool

    def initialize(self):
        return self.lib.initialize()

    def capture(self):
        return self.lib.captureRetina()


class Camera:
    def __init__(self):
        self.lib = ctypes.CDLL(os.path.join(LIB_PATH, "camera.so"))
        self.lib.initialize.restype = ctypes.c_bool
        self.lib.captureImage.restype = ctypes.c_bool

    def initialize(self):
        return self.lib.initialize()

    def capture(self):
        return self.lib.captureImage()
