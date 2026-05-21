from __future__ import annotations

import html
import json
import secrets
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from .approval_node import ApprovalClient
from .biometric import DemoOutcome, DemoPerson, DemoSecurityWorkflow, DemoStep


class DemoWorkflowServer:
    def __init__(self, approval_host: str = "127.0.0.1", approval_port: int = 8765, host: str = "127.0.0.1", port: int = 5050):
        self.host = host
        self.port = port
        self.workflow = DemoSecurityWorkflow()
        self.approval_client = ApprovalClient(approval_host, approval_port)
        self.session_id = secrets.token_hex(8)
        self.person = DemoPerson("Synthetic Demo Voter", "demo-voter-001", "face-token-demo-voter-001")
        self.last_steps: List[DemoStep] = []
        self.last_outcome: Optional[DemoOutcome] = None
        self.last_request_id: Optional[str] = None
        self.audit_log: List[Dict[str, Any]] = []
        self._server: Optional[ThreadingHTTPServer] = None

    def _audit(self, kind: str, details: Dict[str, Any]) -> None:
        self.audit_log.append({"kind": kind, "details": details, "at": time.time()})
        self.audit_log[:] = self.audit_log[-12:]

    def _scan_frames_html(self, frames: List[str], active_index: int) -> str:
        blocks = []
        for index, frame in enumerate(frames):
            active_class = "active" if index == active_index else ""
            blocks.append(f'<div class="scan-line {active_class}">{html.escape(frame)}</div>')
        return "".join(blocks)

    def render(self) -> str:
        fingerprint_panel = "".join(
            f'<div class="chip {"active" if step.stage == "fingerprint" else ""}">{html.escape(step.message)}</div>'
            for step in self.last_steps
            if step.stage == "fingerprint"
        ) or '<div class="placeholder">Fingerprint verification not yet run.</div>'
        retina_panel = "".join(
            f'<div class="chip {"active" if step.stage == "retina" else ""}">{html.escape(step.message)}</div>'
            for step in self.last_steps
            if step.stage == "retina"
        ) or '<div class="placeholder">Retina verification not yet run.</div>'
        face_panel = "".join(
            f'<div class="chip {"active" if step.stage == "face-monitoring" else ""}">{html.escape(step.message)}</div>'
            for step in self.last_steps
            if step.stage == "face-monitoring"
        ) or '<div class="placeholder">Continuous face verification is idle.</div>'
        audit_items = "".join(
            f"<li><strong>{html.escape(item['kind'])}</strong> {html.escape(json.dumps(item['details']))}</li>"
            for item in reversed(self.audit_log)
        ) or "<li>No workflow events yet.</li>"
        approval_status = "pending"
        approval_signature = "n/a"
        if self.last_outcome is not None:
            approval_status = self.last_outcome.decision
            approval_signature = self.last_outcome.signature or "n/a"

        holding_html = ""
        if self.last_request_id:
            holding_html = self.workflow.biometric.holding_screen_html(self.person, self.last_request_id)

        return f"""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta http-equiv="refresh" content="2">
          <title>VoteGuard Demo Workflow</title>
          <style>
            :root {{ --bg: #08111c; --panel: #12243b; --accent: #45d49f; --accent2: #73a7ff; --ink: #eef4ff; --muted: #9db0cb; --danger: #ff6a6a; }}
            body {{ margin: 0; font-family: Arial, sans-serif; background: radial-gradient(circle at top, #17345d, var(--bg)); color: var(--ink); }}
            .wrap {{ max-width: 1200px; margin: 0 auto; padding: 28px; }}
            .hero {{ display:flex; justify-content:space-between; gap: 18px; align-items: stretch; margin-bottom: 20px; }}
            .title {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; }}
            .subtitle {{ color: #c8d4e7; max-width: 760px; line-height: 1.6; }}
            .banner {{ background: linear-gradient(90deg, rgba(69,212,159,.18), rgba(115,167,255,.12)); border: 1px solid rgba(255,255,255,.10); border-radius: 18px; padding: 16px; min-width: 320px; }}
            .layout {{ display:grid; grid-template-columns: 1.5fr 1fr; gap: 18px; }}
            .panel {{ background: rgba(9,17,31,.9); border: 1px solid rgba(255,255,255,.08); border-radius: 18px; padding: 18px; box-shadow: 0 16px 40px rgba(0,0,0,.24); }}
            .card-grid {{ display:grid; gap: 14px; grid-template-columns: repeat(3, minmax(0,1fr)); }}
            .card {{ background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 14px; min-height: 150px; }}
            .card h3 {{ margin-top: 0; }}
            .chip {{ display:inline-block; border-radius: 999px; padding: 8px 12px; margin: 6px 6px 0 0; background: rgba(255,255,255,.08); color: #d7e6ff; }}
            .chip.active {{ background: rgba(69,212,159,.16); border: 1px solid rgba(69,212,159,.45); color: #d9fff0; }}
            .scan-box {{ margin-top: 12px; border-radius: 16px; background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.01)); border: 1px solid rgba(255,255,255,.08); padding: 12px; min-height: 130px; overflow: hidden; position: relative; }}
            .scan-line {{ padding: 8px 10px; border-radius: 12px; margin: 6px 0; background: rgba(255,255,255,.04); opacity: .45; }}
            .scan-line.active {{ opacity: 1; background: rgba(69,212,159,.18); transform: translateX(6px); }}
            .scan-bar {{ height: 4px; border-radius: 999px; background: linear-gradient(90deg, transparent, var(--accent), transparent); animation: slide 1.5s linear infinite; margin-top: 12px; }}
            @keyframes slide {{ from {{ transform: translateX(-60%); }} to {{ transform: translateX(60%); }} }}
            .button-row {{ display:flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }}
            button, .button {{ border: 0; border-radius: 12px; padding: 12px 16px; font-weight: 700; cursor: pointer; text-decoration: none; display:inline-block; }}
            .primary {{ background: var(--accent); color: #062015; }}
            .secondary {{ background: var(--accent2); color: #071225; }}
            .danger {{ background: var(--danger); color: white; }}
            .ghost {{ background: rgba(255,255,255,.09); color: var(--ink); }}
            .list {{ line-height: 1.7; color: #c8d4e7; }}
            .holding-card {{ margin-top: 18px; border-radius: 18px; padding: 18px; border: 1px solid rgba(69,212,159,.35); background: linear-gradient(135deg, rgba(69,212,159,.14), rgba(115,167,255,.08)); }}
            .holding-banner {{ text-transform: uppercase; letter-spacing: .16em; font-size: 12px; color: #aef1d8; }}
            .holding-title {{ font-size: 24px; font-weight: 800; margin-top: 10px; }}
            .holding-subtitle, .holding-meta, .holding-note {{ margin-top: 8px; color: #d9e6f4; }}
            .scan-ring {{ width: 88px; height: 88px; border-radius: 50%; margin-top: 14px; border: 3px solid rgba(69,212,159,.4); border-top-color: transparent; animation: spin 1s linear infinite; }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
            ul {{ padding-left: 18px; line-height: 1.6; }}
            .footer {{ margin-top: 18px; color: #a8b8cd; font-size: 13px; }}
            .status-pill {{ display:inline-block; margin-top: 8px; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,.08); }}
          </style>
        </head>
        <body>
          <div class="wrap">
            <div class="hero">
              <div>
                <div class="title">VoteGuard Demo Workflow</div>
                <div class="subtitle">Academic prototype only. Every biometric step is simulated, every identity is synthetic, and the secondary approval device uses a local-network signed handshake for demonstration.</div>
              </div>
              <div class="banner">
                <div><strong>Simulation Mode:</strong> ON</div>
                <div><strong>Session:</strong> {html.escape(self.session_id)}</div>
                <div class="status-pill">Approval status: {html.escape(approval_status)}</div>
                <div class="status-pill">Signed ack: {html.escape(approval_signature[:24])}</div>
              </div>
            </div>

            <div class="button-row">
              <form method="post" action="/start"><button class="primary" type="submit">Start Demo Session</button></form>
              <form method="post" action="/fingerprint"><button class="secondary" type="submit">Run Fingerprint Verification</button></form>
              <form method="post" action="/retina"><button class="secondary" type="submit">Run Retina Verification</button></form>
              <form method="post" action="/face"><button class="secondary" type="submit">Run Continuous Face Check</button></form>
              <form method="post" action="/hold"><button class="ghost" type="submit">Open Authorization Holding Screen</button></form>
              <form method="post" action="/authorize"><button class="primary" type="submit">Send Approval Request</button></form>
            </div>

            <div class="layout" style="margin-top: 18px;">
              <div class="panel">
                <div class="card-grid">
                  <div class="card">
                    <h3>Fingerprint Scan</h3>
                    <div class="scan-box">{self._scan_frames_html(self.workflow.biometric.fingerprint_frames(), 1)}</div>
                    <div class="scan-bar"></div>
                    <div class="list">{fingerprint_panel}</div>
                  </div>
                  <div class="card">
                    <h3>Retina Scan</h3>
                    <div class="scan-box">{self._scan_frames_html(self.workflow.biometric.retina_frames(), 2)}</div>
                    <div class="scan-bar"></div>
                    <div class="list">{retina_panel}</div>
                  </div>
                  <div class="card">
                    <h3>Face Monitoring</h3>
                    <div class="scan-box"><div class="scan-line active">Camera feed active</div><div class="scan-line">Continuous verification armed</div><div class="scan-line">Unauthorized user blocked</div></div>
                    <div class="scan-bar"></div>
                    <div class="list">{face_panel}</div>
                  </div>
                </div>
                {holding_html}
              </div>
              <div class="panel">
                <h3>Workflow Audit Log</h3>
                <ul>{audit_items}</ul>
                <h3>Current Demo Person</h3>
                <div class="list">
                  <div><strong>Name:</strong> {html.escape(self.person.display_name)}</div>
                  <div><strong>Synthetic ID:</strong> {html.escape(self.person.synthetic_id)}</div>
                  <div><strong>Face Token:</strong> {html.escape(self.person.face_token)}</div>
                </div>
              </div>
            </div>
            <div class="footer">The approval node should be opened on a second device connected to the same hotspot / local network. The workflow uses only demo data and no external biometric or government APIs.</div>
          </div>
        </body>
        </html>
        """

    def start(self) -> None:
        server = self

        class DemoWorkflowHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover
                return

            def _render(self) -> None:
                body = server.render().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                self._render()

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path == "/start":
                    server._audit("demo-start-requested", {"session_id": server.session_id})
                elif parsed.path == "/fingerprint":
                    step = server.workflow.biometric.simulate_fingerprint_verification(server.person, delay_seconds=0.8)
                    server.last_steps = [s for s in server.last_steps if s.stage != "fingerprint"] + [step]
                    server._audit("fingerprint-verified", step.metadata)
                elif parsed.path == "/retina":
                    step = server.workflow.biometric.simulate_retina_verification(server.person, delay_seconds=0.9, succeed=True)
                    server.last_steps = [s for s in server.last_steps if s.stage != "retina"] + [step]
                    server._audit("retina-verified", step.metadata)
                elif parsed.path == "/face":
                    steps = server.workflow.biometric.continuous_face_verification(server.person, cycles=3, delay_seconds=0.25)
                    server.last_steps = [s for s in server.last_steps if s.stage != "face-monitoring"] + steps
                    server._audit("face-monitoring-updated", {"cycles": len(steps)})
                elif parsed.path == "/hold":
                    server._audit("holding-screen-opened", {"session_id": server.session_id})
                elif parsed.path == "/authorize":
                    request = server.approval_client.submit_request(
                        {
                            "session_id": server.session_id,
                            "synthetic_id": server.person.synthetic_id,
                            "display_name": server.person.display_name,
                            "approval_reason": "Demo authorization request",
                            "face_token": server.person.face_token,
                        }
                    )
                    server.last_request_id = request["request_id"]
                    server._audit("approval-request-sent", {"request_id": server.last_request_id})
                    outcome = server.approval_client.wait_for_ack(server.last_request_id, timeout_seconds=0.1)
                    server.last_outcome = DemoOutcome(
                        session_id=server.session_id,
                        approved=outcome.get("status") == "approved",
                        decision=outcome.get("status", "pending"),
                        signature=outcome.get("signature"),
                        approval_request_id=server.last_request_id,
                        steps=server.last_steps,
                    )
                    server._audit("approval-status-polled", {"request_id": server.last_request_id, "status": outcome.get("status")})
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/")
                self.end_headers()

        self._server = ThreadingHTTPServer((self.host, self.port), DemoWorkflowHandler)
        self._server.serve_forever()
