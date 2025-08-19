// Fingerprint Sensor Driver Header (C++)
#pragma once

class FingerprintSensor {
public:
    bool initialize();
    bool captureFingerprint();
};
