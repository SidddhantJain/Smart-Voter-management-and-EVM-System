# Smart Voter Management and EVM System — VoteGuard Pro

A security-first, prototype-grade electronic voting system combining a touchscreen UI, biometric/device integrations, local encrypted vote storage, and a blockchain client placeholder for immutable recording. The repository includes research/design artifacts (Phase 1A), a working PyQt UI flow, hardware driver stubs (C++), ML modules for biometrics, and operations documentation.

---

## 1) Project Overview

- **Purpose:** Provide a tamper-aware, biometric-enabled electronic voting workflow with auditable storage and a path to blockchain-backed receipts.
- **Problems Solved:**
	- Guided voter journey: Aadhaar entry → biometric verification → ballot casting → secure storage → audit receipt.
	- Simulation-friendly: runs without hardware via UI simulation and mocked device layers.
	- Security foundations: secure boot placeholder, encrypted local vote storage, audit logging.
- **Primary Features (from code):**
	- Touchscreen UI (`ui/main_ui.py`, `ui/aadhaar_entry.py`, `ui/biometric_capture.py`, `ui/voting_screen.py`).
	- Hardware manager and biometric/camera integrations (`hardware/device_manager.py`, `hardware/*.cpp` headers; Python FFI in `hardware/biometric.py`).
	- Encrypted local vote storage (`backend/vote_storage.py` with `cryptography.Fernet`).
	- Blockchain client placeholder (`blockchain/client.py`) using `web3`, Rust crypto FFI (`blockchain/crypto_bridge.py`, `blockchain/crypto.rs`).
	- ML modules for recognition/analytics (`ml/*`).
	- Secure boot attestation placeholder (`security/secure_boot.py`).
	- Audit logging (`utils/logger.py`).
- **Tech Stack:**
	- Languages: Python 3.11+, C++ (hardware stubs), Rust (crypto FFI stub).
	- UI: PyQt5.
	- Crypto: `cryptography.Fernet` (local storage), Rust FFI bridge (planned).
	- Blockchain: `web3` client (placeholder, not fully wired), simulated chain (`backend/blockchain_simulation.py`).
	- ML: OpenCV, TensorFlow, NumPy, scikit-learn (in code imports; see “Dependencies” notes).
	- OS Target: Windows (PowerShell), IoT device target envisioned.

---

## 2) Repository Map (Directory & Module Guide)

Top-level
```
Smart Voter management and EVM System/
├─ README.md                       # This document (generated)
├─ run_app.py                      # Root launcher for PyQt UI
├─ votes.json                      # Local vote data (root-level; see also src copy)
├─ key.key                         # Fernet key (local); see security notes
├─ docs/                           # General docs incl. storyboard, diagrams
├─ Phase 1A - Foundation/          # Research, design, and prototype source
├─ *.xml / *.png                   # Architecture/use-case diagrams (draw.io/PlantUML)
```

Phase 1A — Month 3 Prototype (primary codebase)
```
Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/
├─ README.md
├─ requirements.txt
├─ docs/
│  ├─ architecture_diagram_comprehensive.xml
│  ├─ architecture_diagram_drawio.xml
│  ├─ architecture_diagram.puml
│  └─ architecture_diagram.xml
├─ src/
│  ├─ main.py                      # Orchestrator (secure boot → devices → blockchain → UI)
│  ├─ run_app.py                   # Alternative launcher (adds path then ui.main_ui.main())
│  ├─ votes.json                   # Local vote store (duplicate path; see backend)
│  ├─ key.key                      # Fernet key (duplicate path; see security)
│  ├─ ui/
│  │  ├─ main_ui.py               # Stacked PyQt UI (Aadhaar → Biometric → Voting)
│  │  ├─ aadhaar_entry.py         # Aadhaar + Voter ID validation (length checks)
│  │  ├─ biometric_capture.py     # Camera/biometric capture (simulated + OpenCV feed)
│  │  ├─ touchscreen.py           # CLI-ish touchscreen runner driving DeviceManager
│  │  └─ voting_screen.py         # Party selection; persists via backend
│  ├─ backend/
│  │  ├─ vote_storage.py          # Encrypted JSON store with Fernet
│  │  └─ blockchain_simulation.py # Simple PoW chain for vote batches (unused by UI)
│  ├─ blockchain/
│  │  ├─ client.py                # web3-based submission (placeholder)
│  │  ├─ crypto_bridge.py         # ctypes FFI to Rust `crypto.so` (not included)
│  │  └─ crypto.rs                # Rust source (not built; no `.so` in repo)
│  ├─ hardware/
│  │  ├─ device_manager.py        # Initializes and captures fingerprint/retina/camera
│  │  ├─ biometric.py             # ctypes to `*.so` drivers (not included)
│  │  ├─ *.cpp / *.h              # C++ driver stubs (fingerprint, camera, retina, tamper)
│  ├─ ml/
│  │  ├─ arcface_recognition.py   # Loads Keras model; embeddings; compare faces
│  │  ├─ fingerprint_recognition.py# ORB matching of two images
│  │  ├─ anomaly_detection.py     # Threshold calibration; detection
│  │  └─ real_time_analytics.py   # Simulated analytics loop
│  ├─ security/secure_boot.py     # Secure boot check (print-based placeholder)
│  └─ utils/logger.py             # Console + Fernet-encrypted audit log
└─ tests/                          # Empty
```

Research & Design Artifacts
```
Phase 1A - Foundation/
├─ Month 1 - Research & Planning/
│  ├─ Stakeholder_Analysis_Report.md
│  ├─ Regulatory_Compliance_Review.md
│  ├─ Technology_Stack_Finalization.md
│  └─ Team_Assembly_Strategy.md
├─ Month 2 - System Design/
│  ├─ Architecture_Documentation.md
│  ├─ Blockchain_Network_Planning.md
│  ├─ Hardware_Specifications.md
│  └─ Security_Framework_Design.md
└─ Month 3 - Prototype Development/
	 ├─ 1. Core Blockchain Implementation.md
	 └─ EVM IoT Application/ (see above)
```

Entrypoints
- UI launch (root): `run_app.py` → `ui.main_ui.MainUI()`
- Orchestrator (prototype): `Phase 1A - Foundation/.../src/main.py` → devices + blockchain + `TouchscreenUI.run()`
- Touchscreen runner: `Phase 1A - Foundation/.../src/ui/touchscreen.py` (prints/logs flow)

---

## 3) System Architecture

- **Components:** UI (PyQt), Hardware Manager (biometric/camera), Backend Storage (Fernet JSON), Blockchain Client (web3 placeholder + Rust crypto FFI), ML (face/fingerprint/anomaly), Security (secure boot), Utils (logger).
- **Boundaries:**
	- UI ↔ Hardware (capture events via `DeviceManager`).
	- UI ↔ Backend (`VoteStorage.store_vote`).
	- UI ↔ Blockchain (`BlockchainClient.submit_vote` placeholder).
	- ML modules are callable utilities, not fully wired into UI flow.
- **Responsibilities:** UI drives state; backend ensures encrypted persistence; blockchain client prepares hashes/signatures and would post on-chain; hardware manager abstracts sensors.

ASCII Overview
```
[User] → [PyQt UI: Aadhaar → Biometric → Ballot]
							 |                |            
							 v                v            v
				[DeviceManager]   [ML (optional)]   [VoteStorage]
							 |                               |
		 [Fingerprint/Retina/Camera]               v
																							 [Encrypted votes.json] → [Audit log]
																									 |
																									 v
																				 [BlockchainClient (placeholder)]
																				 (hash/sign; planned web3 submit)
```

Mermaid (optional)
```mermaid
flowchart TD
	UI[Aadhaar → Biometric → Ballot]
	DM[DeviceManager]
	HW[Fingerprint/Retina/Camera]
	VS[VoteStorage (Fernet JSON)]
	BC[BlockchainClient (web3+Rust FFI)]
	ML[ML utils]
	LOG[Audit Logger]

	UI --> DM --> HW
	UI --> VS --> LOG
	UI --> BC
	ML -. optional .-> UI
```

Workflows
- **Synchronous:** UI event handlers, device captures, local vote storage.
- **Asynchronous (planned):** Blockchain submission, analytics; currently simulated with print/logs.

---

## 4) Component Breakdown (Deep)

### UI (`src/ui`)
- **MainUI (`main_ui.py`):** `QStackedWidget` managing Aadhaar → Biometric screens; full-screen styling; transitions via index.
- **AadhaarEntryScreen (`aadhaar_entry.py`):** collects 12-digit Aadhaar + Voter ID; simple validation; advances to biometric.
- **BiometricCaptureScreen (`biometric_capture.py`):**
	- Camera feed via OpenCV; anomaly warning for multiple faces (CascadeClassifier).
	- Buttons to simulate fingerprint/retina/face; serial device connection stub; simulation mode fallback.
	- On face capture, transitions to `VotingScreen` with party list.
- **VotingScreen (`voting_screen.py`):** shows parties; on selection, calls `VoteStorage.store_vote` and shows success; returns to Aadhaar.
- **TouchscreenUI (`touchscreen.py`):** non-GUI runner that uses `DeviceManager` and `BlockchainClient` to simulate end-to-end flow and audit logs.

Error/Retry Paths
- Validation failure in Aadhaar: message box warning; remains in screen.
- Camera unavailable: error dialog; prevents start.
- Serial device connection failure: shows error; enables “Simulate Biometric Capture” fallback.
- Vote storage exceptions: handled implicitly via `VoteStorage` (no explicit try/except in UI — consider adding).

Dependencies
- `PyQt5`, `cv2`, `numpy`, `serial` (PySerial), internal backend.

### Backend Storage (`src/backend/vote_storage.py`)
- **Responsibilities:** Encrypted append-only JSON store using `cryptography.Fernet`.
- **Key Functions:**
	- `load_or_generate_key()`: loads `key.key` or creates one.
	- `store_vote(election_type, party_name, timestamp)`: decrypts, appends vote, re-encrypts.
	- `initialize_storage()`: reinitializes encrypted list.
- **Behavior:** Creates `votes.json` on first run as encrypted list. Prints stored vote.
- **Performance:** Small file encryption per write; acceptable for prototype; consider batching.
- **Error Handling:** Minimal; encryption/decryption exceptions would bubble.

### Blockchain (`src/blockchain`)
- **Client (`client.py`):**
	- Uses `web3` to connect (HTTP 8545). Contract address/ABI placeholders; no actual on-chain calls in `submit_vote`.
	- Hashes/signs via Rust FFI (`crypto_bridge.py`), then returns a dict with status/hash/signature.
- **CryptoBridge (`crypto_bridge.py`):** expects compiled `crypto.so` with functions `hash_vote`, `sign_vote`, `generate_keypair`, `verify_signature`. Not present in repository → “Not found in repository”.
- **Simulation (`backend/blockchain_simulation.py`):** independent PoW blockchain demo; unused by UI.

### Hardware (`src/hardware`)
- **DeviceManager:** orchestrates `FingerprintSensor`, `RetinaScanner`, `Camera` (Python FFI).
- **biometric.py:** loads `.so` libraries (`fingerprint_sensor.so`, `retina_scanner.so`, `camera.so`). Not present in repository → “Not found in repository”.
- **C++ stubs:** `.cpp`/`.h` drivers print initialization/capture; no build scripts present.

### ML (`src/ml`)
- **ArcFace:** loads Keras model from path; preprocesses image; computes embeddings; compares with threshold.
- **FingerprintRecognition:** ORB-based image matching simulation; reports success/failure.
- **AnomalyDetection:** percentile-based threshold calibration; detection.
- **RealTimeAnalytics:** simulated loop printing metrics.

### Security (`src/security/secure_boot.py`)
- Print-based secure boot integrity verification placeholder.

### Utils (`src/utils/logger.py`)
- Console logging + writes Fernet-encrypted lines to `audit_log.enc` using a hardcoded key → security risk.

---

## 5) Implementation Details (End-to-End Flow)

- **Entrypoint (root UI):** `run_app.py`
	1. Ensures prototype `src` path in `sys.path`.
	2. Instantiates `MainUI()` and starts `QApplication` loop.
- **UI Flow:**
	- Aadhaar → Biometric → Voting.
	- Voting calls `VoteStorage.store_vote`, which decrypts `votes.json`, appends vote, encrypts.
- **Touchscreen Orchestrator (`src/main.py`):**
	1. `SecureBoot.verify_integrity()` prints success.
	2. `DeviceManager.initialize_all()` calls sensor init.
	3. `BlockchainClient.connect()` prints connected.
	4. `TouchscreenUI.run()` captures devices, logs, simulates selection, calls `BlockchainClient.submit_vote()`.
- **Key Algorithms/Rules:**
	- Aadhaar validation: length=12, numeric.
	- Face anomaly: >1 faces warn.
	- Fernet encryption per vote list write.
- **Configuration & Env Vars:** None defined in repo. Path manipulations exist in `run_app.py`.
- **Feature Flags:** Simulation mode appears in `BiometricCaptureScreen` via `simulate_biometric()`; no global flags.
- **Interfaces/Contracts:** Device FFI expects `.so` libraries with `initialize`/`capture*` functions; Rust crypto expects `crypto.so` functions.

---

## 6) Data Layer & Storage

- **Type:** Encrypted JSON file (`votes.json`) with Fernet.
- **Schema (implicit):** `{ election_type, party_name, timestamp }` per vote.
- **Migrations:** Not applicable (file-based).
- **Indexing/Performance:** No indexes; sequential list; small-scale prototype.
- **Caching:** None.
- **Retention/Cleanup:** `initialize_storage()` resets to empty encrypted list.

---

## 7) API Documentation

Not found in repository.
- No REST/gRPC servers or endpoint definitions present.
- `BlockchainClient` does not expose HTTP APIs; it is a client.

---

## 8) Authentication & Authorization

- **Mechanism:** Not present in repository (no JWT/session/OAuth). UI uses simple local validation (Aadhaar length) and simulated biometrics.
- **Roles/Permissions:** Not present.
- **Token Handling:** Not present.
- **Access Control Enforcement:** UI gating via success states only.

---

## 9) Security Review (Detailed)

Threat Model
- **Assets:** Votes (`votes.json`), audit logs (`audit_log.enc`), Fernet key (`key.key`), device integrity, biometric captures.
- **Actors:** Voters, Admins/Operators, Potential adversaries (tamper, spoofing, malware).
- **Trust Boundaries:** UI ↔ hardware devices; local storage ↔ blockchain client; FFI boundaries (Rust/C++ libraries).

Findings
- **Secrets Management:**
	- `utils/logger.py` uses a hardcoded Fernet key (`b'your-encryption-key'`) → must be replaced with secure secret loading.
	- `key.key` is stored alongside code (both root and `src/`) → move to secure secret store; rotate keys.
- **Supply Chain / Dependencies:**
	- `requirements.txt` missing packages used in code: `web3`, `opencv-python`, `numpy`, `scikit-learn`, `tensorflow`, `pyserial`.
	- No lockfile present; recommend pinning versions.
- **FFI Risks:** `crypto.so` and hardware `.so` libraries are not present → loading will fail; ensure signed binaries and strict path controls.
- **Input Validation:** Aadhaar numeric/length check only; voter ID unchecked; biometric capture simulated. Add strong validation.
- **Logging Sensitivity:** Ensure audit log excludes PII; encrypted log key must be protected.
- **Secure Defaults Checklist:**
	- [ ] No hardcoded keys or secrets.
	- [ ] Enforce least privilege for file access.
	- [ ] Validate all inputs (Aadhaar format, voter ID, image data).
	- [ ] Fail closed on device/crypto load errors.
	- [ ] Pin dependencies; run SCA.

Security TODO (Prioritized)
1. Remove hardcoded key in `utils/logger.py`; load from env/secret vault.
2. Move `key.key` out of repo; add `.gitignore` and secret loading.
3. Add robust validation and error handling paths across UI/Backend.
4. Create a secure `requirements.txt` with all used deps and pin versions; add SCA in CI.
5. Sign and verify FFI libraries; add integrity checks.
6. Implement RBAC for admin-only views (counting, dashboard).

---

## 10) Observability & Operations

- **Logging:** `utils/logger.Logger.log()` prints `[LOG] ...` and writes encrypted entries to `audit_log.enc`. No correlation IDs; recommend adding.
- **Metrics/Tracing:** Not present.
- **Health Checks:** Not present; consider adding device readiness checks and UI heartbeat.
- **Alerting Recommendations:** Set SLOs around device init success rate, vote write latency, camera availability.
- **Failure Modes & Diagnosis:**
	- Missing `.so` libraries → import errors; check `src/hardware` and `src/blockchain` FFI.
	- Camera access denied → OpenCV warnings; verify permissions and device index.
	- Fernet decrypt errors → key mismatch; ensure `key.key` matches `votes.json` encryption.

---

## 11) Deployment

Supported Modes
- **Local Dev:** PyQt UI via root `run_app.py`.
- **Docker:** Not found in repository.
- **Kubernetes:** Not found in repository.
- **Cloud:** Not found in repository.

Build/Run
```powershell
# From repo root (Windows PowerShell)
# 1) Python env (recommended)
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r "Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/requirements.txt"
# Additional packages used in code but missing from requirements:
pip install web3 opencv-python numpy scikit-learn tensorflow pyserial

# 3) Run the PyQt UI
python .\run_app.py

# Alternative orchestrator (prototype runner)
python "Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/src/main.py"
```

Runtime Requirements
- Windows with Python 3.11+, PyQt5, OpenCV camera access, optional compiled `.so`/`.dll` drivers (not provided).

Ports/Volumes/Networking
- No network servers in UI; blockchain client connects to `http://127.0.0.1:8545` (placeholder).

CI/CD
- Not found in repository (no `.github/workflows`, no pipeline files).

Release Strategy
- Not defined; recommend semantic versioning and signed releases.

---

## 12) Configuration Reference

Environment Variables & Config Files

Not found in repository (no `.env`, no config module). Suggested variables:

| Name | Required | Default | Example | Impact |
|------|----------|---------|---------|--------|
| `VOTE_STORAGE_PATH` | Optional | `votes.json` | `C:\\data\\votes.enc` | Where encrypted votes are stored |
| `FERNET_KEY_PATH` | Required | `key.key` | `C:\\secrets\\vote_fernet.key` | Key file for `VoteStorage` |
| `AUDIT_LOG_PATH` | Optional | `audit_log.enc` | `C:\\logs\\audit_log.enc` | Encrypted audit log location |
| `WEB3_PROVIDER_URL` | Optional | `http://127.0.0.1:8545` | `https://rpc.chain.example` | Blockchain node URL |
| `CONTRACT_ADDRESS` | Optional | `0xYourContractAddress` | `0xABC...` | Vote contract address |

`.env.example` (recommended to create)
```dotenv
VOTE_STORAGE_PATH=./votes.json
FERNET_KEY_PATH=./key.key
AUDIT_LOG_PATH=./audit_log.enc
WEB3_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0xYourContractAddress
```

---

## 13) Testing

- **Structure:** `tests/` exists but is empty.
- **Strategy:** Not defined.
- **How to Run:** Not applicable.
- **Gaps:** No unit/integration/e2e tests; UI/FFI-heavy code needs mocks and simulators.
- **Mocking:** Not implemented; recommend mocking hardware and blockchain clients.

---

## 14) Contribution & Development Workflow

Local Setup
```powershell
# Clone, create venv, install deps
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r "Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/requirements.txt"
pip install web3 opencv-python numpy scikit-learn tensorflow pyserial
```

Dev Commands
- Run UI: `python .\run_app.py`
- Orchestrator: `python "Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/src/main.py"`

Branching/Review
- Not found in repository (no documented conventions).

Coding Standards
- Python style: mixed; no linters/formatters configured; recommend `ruff`, `black`, `mypy`.

---

## 15) Troubleshooting

- **ModuleNotFoundError (backend):** Ensure `src` path is in `sys.path` (root `run_app.py` does this).
- **Camera index errors:** Check device presence; adjust index in `biometric_capture.py`.
- **Fernet decrypt failures:** `key.key` mismatch with `votes.json`; reinitialize via `VoteStorage.initialize_storage()` (will erase votes).
- **FFI load errors:** Missing `.so`/`.dll` files for `crypto_bridge.py` or `hardware/biometric.py`; build and place libraries next to Python files.
- **web3 connection refused:** Ensure local node at `127.0.0.1:8545` is running or set `WEB3_PROVIDER_URL`.

---

## 16) Roadmap & Technical Debt (Inferred)

- **TODOs/Placeholders:**
	- Rust `crypto.so` and C++ driver `.so` files are not present.
	- Blockchain contract ABI/address placeholders; no transaction submission.
	- `utils/logger.py` hardcoded key.
	- Missing dependency pins and SCA.
	- Empty `tests/`.
- **Hardcoded Configs:** Provider URL, contract address, key paths.
- **Fragile Areas:** Path manipulation in `src/run_app.py`; error handling around encryption/IO.
- **Prioritized Improvements:** Security fixes (secrets), dependency pinning, proper DI/config, test coverage, CI, on-chain integration.

---

## 17) Appendix

Glossary
- **Fernet:** Symmetric encryption providing authenticated encryption.
- **FFI:** Foreign Function Interface; cross-language calls (Python→Rust/C++).
- **ArcFace:** Face recognition model producing embeddings for similarity comparison.

Dependency Summary
- From `requirements.txt`: `pyqt5`, `requests`, `cryptography`, `protobuf`, `grpcio`.
- Used in code but missing: `web3`, `opencv-python`, `numpy`, `scikit-learn`, `tensorflow`, `pyserial`.

License
- Not found in repository.

---

### References (Repo Paths)
- UI: `Phase 1A - Foundation/Month 3 - Prototype Development/EVM IoT Application/src/ui/`
- Backend: `.../src/backend/vote_storage.py`
- Blockchain: `.../src/blockchain/client.py`, `.../src/blockchain/crypto_bridge.py`
- Hardware: `.../src/hardware/`
- ML: `.../src/ml/`
- Security: `.../src/security/secure_boot.py`
- Logger: `.../src/utils/logger.py`
- Diagrams: `docs/`, `.../EVM IoT Application/docs/`

---

## Documentation Index
For a structured navigation of project documents and diagrams, see `docs/README.md`.
