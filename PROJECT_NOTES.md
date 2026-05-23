# Smart Voter Management & EVM System — Project Notes

## Executive Summary

- **Project:** Smart Voter Management & EVM System — secure, auditable electronic voting platform combining voter management, biometric verification, camera/ML detection, and an append-only ledger for votes and audits.
- **Value proposition:** tamper-evident vote recording, verifiable tallying, strong voter authentication, and clear auditability for election integrity.

## Objectives

- **Primary goal:** Correct, private, and auditable recording and counting of votes.
- **Security goals:** Integrity, non-repudiation, voter privacy, and resilience against replay/fraud.
- **Operational goals:** Usability on constrained EVM devices, offline resilience, and clear audit trails.
- **Regulatory goals:** Produce compliance-ready logs and artifacts for post-election audits.

## High-level Architecture

- **Layers:**
  - UI/API layer (voting front-end & `voteguard/app.py`).
  - Adapters (hardware, biometric sensors, camera). 
  - Core logic (voter/session state machine, ballot workflow).
  - Persistence (local JSON ledgers + optional blockchain backend).
  - ML/camera module (detection & liveness).
- **Data flow:** Voter → Authentication → Ballot display → Cast → Ledger write → Tally & Audit.
- **Patterns:** Modular adapters, pluggable ledger backends, append-only storage for resilience.

## Components & Responsibilities

- **Voter Management:** registration, eligibility, session lifecycle and mapping to pseudonymous ballot IDs.
- **Biometric Adapter:** enrollment, template storage (encrypted), match scoring and policy thresholds.
- **Camera/ML Module:** face detection, liveness classification, quality scoring, and audit image capture policy.
- **Ledger Layer:** cast registry, ballot ledger, audit ledger, and cryptographic chaining (hash pointers).
- **Tallying Engine:** deterministic counting, duplicate detection and invalid ballot handling.
- **Audit Tools:** ledger verification, `scripts/verify_ledger.py`, and reconciliation utilities.
- **Admin Interfaces:** candidate & election config, start/stop controls, and admin audit logs.

## Data Model & Ledger Design

- **Principles:** minimize PII, separate identity from ballot payloads, use cryptographic chaining for tamper evidence.
- **Cast registry (example fields):**
  - `ballot_id` (pseudonymous UUID)
  - `timestamp`
  - `candidate_selection` (encrypted or reference)
  - `device_id`
  - `prev_hash`
  - `entry_hash` = SHA-256(prev_hash || timestamp || payload || device_nonce)
- **Ballot ledger:** stores encrypted ballot payloads or references to payloads held securely.
- **Audit ledger:** events (auth success/fail, admin actions) and synchronization records.

## Voting Process & State Machine

- **Primary states:** Idle → Ready → Authenticating → Authenticated → BallotDisplayed → Casting → CastConfirmed → Completed / Rejected / Error.
- **Key transitions & rules:**
  - Timeouts for authentication and ballot selection.
  - Retry and lockout policy for biometric failures.
  - Offline behavior: append locally, mark unsynced, reconcile on network restore.
- **Edge cases:** interrupted cast, conflicting ledger entries, ambiguous matches — documented fallback flows.

## Use Cases

- **In-person voting (primary):** ID presentation → biometric + liveness check → ballot displayed → voter confirms → ledger append → confirmation/receipt.
- **Assisted voting:** admin-assisted input with observer logging and multi-party confirmation.
- **Enrollment:** capture demographic + biometric template, store encrypted templates and enrollment logs.
- **Audit & recount:** auditors verify chain integrity, generate inclusion proofs, and run reconciliation.

## Biometrics, Camera & ML Integration

- **Biometric logic:** template-based matching with configurable thresholds; enroll/verify separation; secure template encryption.
- **Camera/ML:** detection → liveness classifier → quality checks; small, optimized models for on-device inference.
- **Privacy:** avoid raw image retention by default; if retained for audit, encrypt and set retention durations.
- **Performance & UX:** aim for sub-second auth latency; provide graceful fallback if ML modules fail.

## Tallying, Verification & Audits

- **Tallying:** read valid cast registry entries; dedupe ballots; exclude invalidated entries; deterministic sorting for reproducibility.
- **Proofs & verifiability:** support inclusion proofs (hash chaining) and exportable signed summaries for third-party verification.
- **Audit procedure:** verify chain hashes, cross-check counts, review authentication logs and sync records.

## Security & Threat Model

- **Threats covered:** device compromise, insider manipulation, replay, biometric spoofing, ledger tampering, DoS.
- **Mitigations:**
  - Append-only chaining, signed ledger exports, device signing keys.
  - Role-based admin controls and immutable audit logs.
  - TLS for sync, encryption at rest, secure enrollment and key management.
  - ML robustness testing and liveness detection to mitigate spoofing.
- **Residual risks:** hardware root compromise, supply-chain attacks — reduce via physical security and chain-of-custody.

### CI/CD and security-testing practices

- **Secure CI configuration:**
  - Enforce branch protection, required status checks, and code owners for critical paths.
  - Use ephemeral runners for untrusted PRs and sandbox execution for integration tests.
  - Do not store secrets in repo; use secret managers with scoped access and rotation policies.

- **Automated security checks in pipeline:**
  - **Dependency scanning:** `pip-audit`, Snyk, or Dependabot to block known CVEs.
  - **SAST:** Bandit for Python, custom rules for crypto misuse and insecure file handling.
  - **DAST/pen-test hooks:** run automated web/API scanners against staging before production deploy.
  - **Container/image scanning:** scan container images for OS/vulnerability issues before publishing.

- **Release hardening:**
  - Sign release artifacts and maintain reproducible builds where possible.
  - Maintain a published changelog and signed SBOM (software bill of materials) for audits.

- **Access control & auditability:**
  - Limit who can approve production deploys; require multi-person approval for critical releases.
  - Log all CI/CD actions into immutable logs that feed into the audit ledger.

- **Penetration testing & red team:** schedule regular third-party pen-tests and incorporate findings into backlog; run internal fuzzing for critical parsers and ledger handling code.

- **Incident response in CI/CD context:**
  - Revoke compromised secrets, rotate keys, and trigger artifact revocation in registries.
  - Keep emergency rollback playbooks and validated restore procedures for ledger recovery.

## Privacy & Compliance

- **Data minimization:** store only necessary attributes; pseudonymize ballot references.
- **Retention & purge:** defined retention windows for images/biometric data; automated purging and secure deletion.
- **Transparency:** enrollment consent logs and human-readable privacy statements included in audit pack.

## Testing & Validation Strategy

- **Unit tests:** state machine, ledger hashing, tally functions (`tests/test_state_machine.py`, `tests/test_ledger.py`).
- **Integration tests:** end-to-end casting, offline reconciliation (`scripts/simulate_votes.py`, test harnesses).
- **ML tests:** FAR/FRR metrics, dataset validation, adversarial scenarios.
- **System tests:** load tests on expected electorate size; bench auth latency and throughput.
- **CI:** run unit + integration + model validation on PRs; sign release artifacts.

### Expanded testing & pipeline details

- **CI pipeline stages (recommended):**
  1. **Pre-commit checks:** linting, formatting, static type checks.
  2. **Unit tests:** fast unit test suite with coverage thresholds.
  3. **Security scans:** dependency vulnerability scan (e.g., `pip-audit`), secret scanning, SAST (Bandit).
  4. **Integration tests:** run integration harness in ephemeral test environment including offline/restore flows.
  5. **Model validation:** verify model metrics (FAR/FRR) against acceptance thresholds and check model signature.
  6. **Build & artifact signing:** build artifacts (wheels, containers), sign artifacts and upload to registry.
  7. **Deploy to staging:** deploy via IaC to staging and run smoke tests.
  8. **Canary/production rollout:** gated deploy with monitoring and automated rollback.

- **Test automation recommendations:**
  - Keep unit tests fast and isolate external deps with mocks.
  - Run heavier integration and security scans nightly to avoid blocking PRs.
  - Store model cards and validation results alongside artifacts.

- **Metrics & monitoring:** track coverage, test flakiness, auth latency, ledger write latency, and model metric trends.

- **Continuous verification:** schedule nightly full-integration runs, DAST scans, and ledger integrity checks.

## Deployment & Operations

- **Provisioning:** secure device enrollment, signed config bundles, and key injection procedures.
- **Updates:** signed OTA updates for software and ML models.
- **Monitoring:** auth rates, error counts, unsynced ledger entries; central ops dashboard for health.
- **Backup & recovery:** periodic encrypted ledger export, checksums, and verified restores.

## Limitations & Assumptions

- **Assumptions:** trustworthy central reconciliation authority, available secure hardware for signing.
- **Limitations:** biometric errors, ML bias, potential privacy trade-offs for image retention.
- **Operational constraints:** bandwidth and power limitations at remote polling sites.

## Future Work & Recommendations

- **Hardening:** TPM-backed device keys and hardware attestation.
- **Advanced verifiability:** threshold cryptography, homomorphic tallying, or mixnets for end-to-end verifiability.
- **Ledger choices:** evaluate permissioned blockchain vs centralized signed append-only logs for performance and governance.
- **Accessibility & UX:** refine assisted voting, localization, and accessibility testing.

## Appendix — Artifacts to Include in Report

- Architecture diagram (sequence and component diagrams).
- State-machine diagram and sample JSON schemas for ledgers.
- Sample anonymized ledger exports and verification guide.
- Model card(s) for ML components: training data summary, metrics (FAR/FRR), and intended use.

## Quick run & verification (local)

1. Create virtual environment and install requirements.

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-base.txt
```

2. Start the application (example):

```bash
python run_app.py
```

3. Run ledger verification script:

```bash
python scripts/verify_ledger.py
```

---

If you want this exported as a PDF, or prefer an expanded section (diagrams, JSON schemas, or inline file references to specific code), tell me which sections to expand and I will update `PROJECT_NOTES.md` accordingly.
