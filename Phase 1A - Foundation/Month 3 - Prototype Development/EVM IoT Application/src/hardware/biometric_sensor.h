// Biometric Sensor Driver Header (C++)
#pragma once

class BiometricSensor {
public:
    bool initialize();
    bool captureFingerprint();
    bool captureIris();
};
