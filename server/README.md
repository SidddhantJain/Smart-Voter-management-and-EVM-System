# VoteGuard Verification Server

Run this on the approval/server laptop.

```powershell
python -m server.run_server --web-port 8085 --socket-port 8785
```

Capabilities:
- 3-way acknowledgment tracking
- Aadhaar and voter ID format checks
- Device readiness checks
- Biometric and face verification gating
- Signed approval / rejection payloads

The client laptop can connect using the socket API exposed on the TCP port.
