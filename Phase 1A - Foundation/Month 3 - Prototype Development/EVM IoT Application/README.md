# VoteGuard Pro EVM IoT Application

## Overview
This directory contains the source code and documentation for the base application that will be installed on the custom IoT hardware device (EVM unit) for the VoteGuard Pro system.

## Purpose
- Provide a secure, tamper-evident, and user-friendly interface for electronic voting
- Integrate with biometric sensors, camera, GPS, and tamper detection hardware
- Communicate securely with the VoteGuard Pro blockchain network for vote recording and verification
- Support real-time device health monitoring and audit logging

## Key Features
- Multi-factor voter authentication (biometric, OTP, device trust)
- Secure ballot interface for candidate selection and vote confirmation
- Blockchain integration for immutable vote storage and receipt generation
- Hardware tamper detection and alerting
- Local audit trail and encrypted log storage
- Modular design for future hardware expansion

## Technology Stack
- **Programming Language:** Python (for rapid prototyping and hardware integration)
- **UI Framework:** PyQt5 or Kivy (touchscreen interface)
- **Hardware Integration:** GPIO, USB, serial (for sensors and peripherals)
- **Blockchain Client:** gRPC/REST API to VoteGuard Pro backend
- **Security:** AES-256 encryption, secure boot, device attestation

## Directory Structure
```
EVM IoT Application/
├── src/                # Application source code
│   ├── main.py         # Main entry point
│   ├── ui/             # UI components (touchscreen)
│   ├── hardware/       # Sensor and device drivers
│   ├── blockchain/     # Blockchain client integration
│   ├── security/       # Security and cryptography modules
│   └── utils/          # Utility functions
├── tests/              # Unit and integration tests
├── requirements.txt    # Python dependencies
├── README.md           # Project overview (this file)
└── docs/               # Technical documentation
```

## Next Steps
1. Define hardware abstraction layer and device interface contracts
2. Scaffold main application and UI workflow
3. Implement secure device registration and blockchain connectivity
4. Integrate biometric and tamper detection modules
5. Develop secure ballot casting and receipt generation logic
6. Establish local and remote audit logging

---

**For hardware specifications and integration details, see the System Architecture and Hardware Specifications documents in Phase 1A Month 2.**
