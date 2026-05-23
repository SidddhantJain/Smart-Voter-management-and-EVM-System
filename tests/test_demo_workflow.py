from __future__ import annotations

import threading
import time

from voteguard.demo.approval_node import ApprovalClient, MockApprovalNode
from voteguard.demo.biometric import DemoPerson, SimulatedBiometricWorkflow


def test_simulated_biometrics_return_successful_mock_results():
    workflow = SimulatedBiometricWorkflow(simulation_mode=True)
    person = DemoPerson("Synthetic Demo Voter", "demo-voter-001", "face-token-demo-voter-001")

    fingerprint = workflow.simulate_fingerprint_verification(person, delay_seconds=0)
    retina = workflow.simulate_retina_verification(person, delay_seconds=0, succeed=True)
    face_steps = workflow.continuous_face_verification(person, cycles=2, delay_seconds=0)

    assert fingerprint.status == "verified"
    assert fingerprint.message == "Fingerprint Verified"
    assert retina.status == "verified"
    assert len(face_steps) == 2
    assert all(step.status == "verified" for step in face_steps)


def test_socket_handshake_and_signed_ack(tmp_path):
    node = MockApprovalNode(host="127.0.0.1", web_port=0, socket_port=0, secret="demo-secret")

    # Start only the socket listener on an ephemeral port for the handshake test.
    import socketserver

    class TestSocketServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    class TestSocketHandler(socketserver.StreamRequestHandler):
        def handle(self):
            import json
            payload = json.loads(self.rfile.readline().decode("utf-8"))
            action = payload.get("action")
            try:
                if action == "submit":
                    response = node.submit_request(payload.get("payload", {}))
                elif action == "status":
                    response = node.get_status(str(payload.get("request_id", "")))
                elif action == "list":
                    response = {"requests": node.list_requests()}
                elif action == "decision":
                    response = node.decide(
                        str(payload.get("request_id", "")),
                        str(payload.get("decision", "")),
                        str(payload.get("decision_by", "test-approver")),
                    )
                else:
                    response = {"error": f"unknown action: {action}"}
            except Exception as exc:
                response = {"error": str(exc)}
            self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))

    server = TestSocketServer(("127.0.0.1", 0), TestSocketHandler)
    node.socket_port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    client = ApprovalClient(host="127.0.0.1", socket_port=node.socket_port, timeout_seconds=2)
    request = client.submit_request(
        {
            "session_id": "session-1",
            "synthetic_id": "demo-voter-001",
            "display_name": "Synthetic Demo Voter",
            "approval_reason": "demo",
            "face_token": "face-token-demo-voter-001",
        }
    )
    decided = node.decide(request["request_id"], "approve")
    status = client.wait_for_ack(request["request_id"], timeout_seconds=1)

    assert request["status"] == "pending"
    assert decided["status"] == "approved"
    assert status["status"] == "approved"
    assert status["signature"]

    server.shutdown()
