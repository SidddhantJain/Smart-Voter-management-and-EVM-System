from __future__ import annotations

import html
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..adapters.audit_helper import SafeAuditLogger

SIMULATION_MODE = True


@dataclass(frozen=True)
class DemoPerson:
    display_name: str
    synthetic_id: str
    face_token: str


@dataclass(frozen=True)
class DemoStep:
    stage: str
    status: str
    message: str
    at: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DemoOutcome:
    session_id: str
    approved: bool
    decision: str
    signature: Optional[str]
    approval_request_id: Optional[str]
    steps: List[DemoStep]


class SimulatedBiometricWorkflow:
    def __init__(self, simulation_mode: bool = SIMULATION_MODE, logger: Optional[SafeAuditLogger] = None):
        self.simulation_mode = simulation_mode
        self.logger = logger or SafeAuditLogger()
        # optional trained recognizer
        try:
            import cv2
            model_path = Path(__file__).resolve().parent / "models" / "face_recognizer.xml"
            labels_path = Path(__file__).resolve().parent / "models" / "labels.json"
            if model_path.exists() and labels_path.exists():
                self._recognizer = cv2.face.LBPHFaceRecognizer_create()
                self._recognizer.read(str(model_path))
                import json

                with labels_path.open("r", encoding="utf-8") as fh:
                    self._labels = json.load(fh)
            else:
                self._recognizer = None
                self._labels = {}
        except Exception:
            self._recognizer = None
            self._labels = {}

    def fingerprint_frames(self) -> List[str]:
        return [
            "Scanning fingerprint |",
            "Scanning fingerprint /",
            "Scanning fingerprint -",
            "Scanning fingerprint \\",
        ]

    def retina_frames(self) -> List[str]:
        return [
            "Retina scan |",
            "Retina scan /",
            "Retina scan -",
            "Retina scan \\",
        ]

    def simulate_fingerprint_verification(self, person: DemoPerson, delay_seconds: float = 1.5) -> DemoStep:
        self.logger.log("DEMO_FINGERPRINT_SCAN_STARTED", {"synthetic_id": person.synthetic_id})
        if self.simulation_mode and delay_seconds > 0:
            time.sleep(delay_seconds)
        self.logger.log("DEMO_FINGERPRINT_VERIFIED", {"synthetic_id": person.synthetic_id})
        return DemoStep(
            stage="fingerprint",
            status="verified",
            message="Fingerprint Verified",
            at=time.time(),
            metadata={"synthetic_id": person.synthetic_id, "display_name": person.display_name},
        )

    def simulate_retina_verification(
        self,
        person: DemoPerson,
        delay_seconds: float = 1.8,
        succeed: bool = True,
    ) -> DemoStep:
        self.logger.log("DEMO_RETINA_SCAN_STARTED", {"synthetic_id": person.synthetic_id})
        if self.simulation_mode and delay_seconds > 0:
            time.sleep(delay_seconds)
        status = "verified" if succeed else "rejected"
        message = "Retina Verified" if succeed else "Retina Verification Failed"
        self.logger.log("DEMO_RETINA_RESULT", {"synthetic_id": person.synthetic_id, "status": status})
        return DemoStep(
            stage="retina",
            status=status,
            message=message,
            at=time.time(),
            metadata={"synthetic_id": person.synthetic_id, "display_name": person.display_name},
        )

    def continuous_face_verification(
        self,
        person: DemoPerson,
        cycles: int = 3,
        delay_seconds: float = 0.35,
    ) -> List[DemoStep]:
        steps: List[DemoStep] = []
        for index in range(max(1, cycles)):
            if self.simulation_mode and delay_seconds > 0:
                time.sleep(delay_seconds)
            self.logger.log(
                "DEMO_FACE_MONITORING_CYCLE",
                {"synthetic_id": person.synthetic_id, "cycle": index + 1},
            )
            steps.append(
                DemoStep(
                    stage="face-monitoring",
                    status="verified",
                    message=f"Continuous face verification cycle {index + 1} passed",
                    at=time.time(),
                    metadata={"cycle": index + 1, "synthetic_id": person.synthetic_id},
                )
            )
        return steps

    def holding_screen_html(self, person: DemoPerson, request_id: str) -> str:
        return f"""
        <div class="holding-card">
          <div class="holding-banner">Authorization Holding Screen</div>
          <div class="scan-ring"></div>
          <div class="holding-title">Awaiting second-device approval</div>
          <div class="holding-subtitle">{html.escape(person.display_name)} is paused while the remote approver signs off.</div>
          <div class="holding-meta">Request ID: <strong>{html.escape(request_id)}</strong></div>
          <div class="holding-note">Continuous face verification remains active until approval is received.</div>
        </div>
        """


class DemoSecurityWorkflow:
    def __init__(self, biometric: Optional[SimulatedBiometricWorkflow] = None, logger: Optional[SafeAuditLogger] = None):
        self.biometric = biometric or SimulatedBiometricWorkflow()
        self.logger = logger or SafeAuditLogger()

    def run_demo_session(
        self,
        person: DemoPerson,
        approval_client,
        approval_reason: str = "Synthetic demo approval request",
    ) -> DemoOutcome:
        session_id = uuid.uuid4().hex
        steps: List[DemoStep] = []

        self.logger.log("DEMO_SESSION_STARTED", {"session_id": session_id, "synthetic_id": person.synthetic_id})
        steps.append(self.biometric.simulate_fingerprint_verification(person))
        steps.append(self.biometric.simulate_retina_verification(person))
        steps.extend(self.biometric.continuous_face_verification(person, cycles=4))

        request_payload = {
            "session_id": session_id,
            "synthetic_id": person.synthetic_id,
            "display_name": person.display_name,
            "approval_reason": approval_reason,
            "face_token": person.face_token,
        }
        self.logger.log("DEMO_APPROVAL_REQUEST_PREPARED", request_payload)
        request = approval_client.submit_request(request_payload)
        request_id = request["request_id"]
        self.logger.log("DEMO_APPROVAL_REQUEST_SENT", {"session_id": session_id, "request_id": request_id})

        ack = approval_client.wait_for_ack(request_id, timeout_seconds=60)
        decision = ack.get("status", "pending")
        approved = decision == "approved"
        signature = ack.get("signature")
        self.logger.log(
            "DEMO_APPROVAL_DECISION",
            {"session_id": session_id, "request_id": request_id, "decision": decision},
        )

        return DemoOutcome(
            session_id=session_id,
            approved=approved,
            decision=decision,
            signature=signature,
            approval_request_id=request_id,
            steps=steps,
        )
