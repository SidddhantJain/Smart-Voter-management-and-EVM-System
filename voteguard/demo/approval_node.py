from __future__ import annotations

import hmac
import html
import json
import secrets
import socket
import socketserver
import threading
import time
from dataclasses import dataclass, field
from hashlib import sha256
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse


@dataclass
class ApprovalRecord:
    request_id: str
    session_id: str
    synthetic_id: str
    display_name: str
    approval_reason: str
    face_token: str
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    decided_at: Optional[float] = None
    decision_by: Optional[str] = None
    signature: Optional[str] = None
    audit_note: Optional[str] = None


class MockApprovalNode:
    def __init__(
        self,
        host: str = "0.0.0.0",
        web_port: int = 8081,
        socket_port: int = 8765,
        secret: Optional[str] = None,
    ):
        self.host = host
        self.web_port = web_port
        self.socket_port = socket_port
        self.secret = secret or secrets.token_hex(24)
        self._lock = threading.Lock()
        self._records: Dict[str, ApprovalRecord] = {}
        self._audit_events: List[Dict[str, Any]] = []
        self._http_server: Optional[ThreadingHTTPServer] = None
        self._socket_server: Optional[socketserver.ThreadingTCPServer] = None
        self._threads: List[threading.Thread] = []

    @property
    def web_url(self) -> str:
        return f"http://{self.host}:{self.web_port}"

    def _audit(self, kind: str, details: Dict[str, Any]) -> None:
        event = {"kind": kind, "details": details, "at": time.time()}
        self._audit_events.append(event)
        if len(self._audit_events) > 50:
            self._audit_events = self._audit_events[-50:]

    def _canonical_signature(self, record: ApprovalRecord) -> str:
        payload = json.dumps(
            {
                "request_id": record.request_id,
                "session_id": record.session_id,
                "synthetic_id": record.synthetic_id,
                "display_name": record.display_name,
                "status": record.status,
                "decided_at": record.decided_at,
                "decision_by": record.decision_by,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()

    def submit_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request_id = secrets.token_hex(8)
        record = ApprovalRecord(
            request_id=request_id,
            session_id=str(payload.get("session_id", "")),
            synthetic_id=str(payload.get("synthetic_id", "synthetic-user")),
            display_name=str(payload.get("display_name", "Synthetic User")),
            approval_reason=str(payload.get("approval_reason", "Demo request")),
            face_token=str(payload.get("face_token", "face-token")),
        )
        with self._lock:
            self._records[request_id] = record
        self._audit("approval-request-received", {"request_id": request_id, "synthetic_id": record.synthetic_id})
        return self._record_to_dict(record)

    def decide(self, request_id: str, decision: str, decision_by: str = "local-approver") -> Dict[str, Any]:
        with self._lock:
            record = self._records[request_id]
            record.status = "approved" if decision == "approve" else "rejected"
            record.decided_at = time.time()
            record.decision_by = decision_by
            record.signature = self._canonical_signature(record)
            record.audit_note = f"{record.status} by {decision_by}"
            self._records[request_id] = record
        self._audit(
            "approval-decision-made",
            {"request_id": request_id, "decision": record.status, "decision_by": decision_by},
        )
        return self._record_to_dict(record)

    def get_status(self, request_id: str) -> Dict[str, Any]:
        with self._lock:
            record = self._records[request_id]
            return self._record_to_dict(record)

    def list_requests(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self._record_to_dict(record) for record in self._records.values()]

    def _record_to_dict(self, record: ApprovalRecord) -> Dict[str, Any]:
        return {
            "request_id": record.request_id,
            "session_id": record.session_id,
            "synthetic_id": record.synthetic_id,
            "display_name": record.display_name,
            "approval_reason": record.approval_reason,
            "face_token": record.face_token,
            "status": record.status,
            "created_at": record.created_at,
            "decided_at": record.decided_at,
            "decision_by": record.decision_by,
            "signature": record.signature,
            "audit_note": record.audit_note,
        }

    def render_dashboard(self) -> str:
        cards = []
        for record in sorted(self.list_requests(), key=lambda item: item["created_at"], reverse=True):
            decision_controls = ""
            if record["status"] == "pending":
                decision_controls = f"""
                <form method="post" action="/decision" class="decision-form">
                  <input type="hidden" name="request_id" value="{html.escape(record['request_id'])}">
                  <button class="approve" name="decision" value="approve">Approve</button>
                  <button class="reject" name="decision" value="reject">Reject</button>
                </form>
                """
            cards.append(
                f"""
                <div class="request-card {record['status']}">
                  <div class="request-header">
                    <span class="badge">{html.escape(record['status']).upper()}</span>
                    <strong>{html.escape(record['display_name'])}</strong>
                  </div>
                  <div class="request-body">
                    <div><span>Request ID</span><code>{html.escape(record['request_id'])}</code></div>
                    <div><span>Session ID</span><code>{html.escape(record['session_id'])}</code></div>
                    <div><span>Reason</span>{html.escape(record['approval_reason'])}</div>
                    <div><span>Signature</span>{html.escape(record['signature'] or 'pending')}</div>
                  </div>
                  {decision_controls}
                </div>
                """
            )

        audit_items = "".join(
            f"<li><strong>{html.escape(event['kind'])}</strong> {html.escape(json.dumps(event['details']))}</li>"
            for event in reversed(self._audit_events[-8:])
        )

        return f"""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta http-equiv="refresh" content="2">
          <title>VoteGuard Demo Approval Node</title>
          <style>
            :root {{ --bg: #09111f; --panel: #13233d; --ink: #e8f1ff; --accent: #43d9a3; --warn: #ffce54; --danger: #ff6b6b; }}
            body {{ margin: 0; font-family: Arial, sans-serif; background: radial-gradient(circle at top, #17345d, var(--bg)); color: var(--ink); }}
            .wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px; }}
            .hero {{ display:flex; justify-content:space-between; align-items:center; gap: 16px; margin-bottom: 24px; }}
            .title {{ font-size: 30px; font-weight: 800; }}
            .subtitle {{ opacity: .8; max-width: 700px; }}
            .banner {{ background: linear-gradient(90deg, rgba(67,217,163,.18), rgba(67,217,163,.05)); border: 1px solid rgba(67,217,163,.35); padding: 12px 16px; border-radius: 14px; }}
            .grid {{ display: grid; grid-template-columns: 1.8fr 1fr; gap: 20px; }}
            .panel {{ background: rgba(9,17,31,.88); border: 1px solid rgba(255,255,255,.08); border-radius: 18px; padding: 18px; box-shadow: 0 16px 40px rgba(0,0,0,.24); }}
            .request-list {{ display: grid; gap: 14px; }}
            .request-card {{ border-radius: 16px; padding: 16px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); }}
            .request-card.approved {{ border-color: rgba(67,217,163,.5); }}
            .request-card.rejected {{ border-color: rgba(255,107,107,.45); }}
            .badge {{ display:inline-block; font-size: 12px; letter-spacing: .12em; padding: 5px 9px; border-radius: 999px; background: rgba(255,255,255,.08); margin-right: 10px; }}
            .request-body {{ display:grid; gap: 8px; margin-top: 10px; color: #c6d7ef; }}
            .request-body span {{ display:inline-block; width: 100px; color: #8ea5ca; }}
            code {{ background: rgba(0,0,0,.2); padding: 3px 6px; border-radius: 8px; }}
            .decision-form {{ display:flex; gap: 10px; margin-top: 12px; }}
            button {{ border: 0; border-radius: 12px; padding: 10px 16px; font-weight: 700; cursor: pointer; }}
            .approve {{ background: var(--accent); color: #072013; }}
            .reject {{ background: var(--danger); color: white; }}
            ul {{ padding-left: 18px; line-height: 1.6; }}
            .footer {{ margin-top: 18px; opacity: .75; font-size: 13px; }}
          </style>
        </head>
        <body>
          <div class="wrap">
            <div class="hero">
              <div>
                <div class="title">VoteGuard Demo Approval Node</div>
                <div class="subtitle">Local-network only mock approval device. Requests arrive over socket, decisions are signed, and every action is audit logged.</div>
              </div>
              <div class="banner">Signed acknowledgments • Approve / Reject • Synthetic test identities only</div>
            </div>
            <div class="grid">
              <div class="panel request-list">
                {''.join(cards) if cards else '<div class="request-card"><strong>No pending requests.</strong><div class="request-body"><div>Waiting for a demo workflow to submit an approval request.</div></div></div>'}
              </div>
              <div class="panel">
                <h3>Audit Feed</h3>
                <ul>{audit_items if audit_items else '<li>No audit events yet.</li>'}</ul>
              </div>
            </div>
            <div class="footer">Web UI refreshes automatically every 2 seconds. Requests can also be submitted using the socket client from the main demo device.</div>
          </div>
        </body>
        </html>
        """

    def start(self) -> None:
        node = self

        class DemoHTTPRequestHandler(BaseHTTPRequestHandler):
            def _send_html(self, html_text: str, status: int = 200) -> None:
                encoded = html_text.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
                encoded = json.dumps(payload, indent=2).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover
                return

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path in {"/", "/index.html"}:
                    self._send_html(node.render_dashboard())
                    return
                if parsed.path == "/api/requests":
                    self._send_json({"requests": node.list_requests()})
                    return
                if parsed.path == "/api/request":
                    params = parse_qs(parsed.query)
                    request_id = params.get("request_id", [""])[0]
                    if not request_id:
                        self._send_json({"error": "request_id is required"}, status=HTTPStatus.BAD_REQUEST)
                        return
                    try:
                        self._send_json(node.get_status(request_id))
                    except KeyError:
                        self._send_json({"error": "unknown request"}, status=HTTPStatus.NOT_FOUND)
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                content_length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(content_length).decode("utf-8")
                fields = parse_qs(body)
                request_id = fields.get("request_id", [""])[0]
                decision = fields.get("decision", [""])[0]
                if parsed.path == "/decision" and request_id and decision in {"approve", "reject"}:
                    try:
                        node.decide(request_id, decision)
                        self.send_response(HTTPStatus.SEE_OTHER)
                        self.send_header("Location", "/")
                        self.end_headers()
                    except KeyError:
                        self.send_error(HTTPStatus.NOT_FOUND)
                    return
                if parsed.path == "/api/decision" and request_id and decision in {"approve", "reject"}:
                    try:
                        self._send_json(node.decide(request_id, decision))
                    except KeyError:
                        self._send_json({"error": "unknown request"}, status=HTTPStatus.NOT_FOUND)
                    return
                self.send_error(HTTPStatus.BAD_REQUEST)

        class DemoHTTPServer(ThreadingHTTPServer):
            allow_reuse_address = True

        class DemoSocketServer(socketserver.ThreadingTCPServer):
            allow_reuse_address = True

        class DemoSocketHandler(socketserver.StreamRequestHandler):
            def handle(self) -> None:
                raw = self.rfile.readline().decode("utf-8").strip()
                if not raw:
                    return
                try:
                    payload = json.loads(raw)
                    action = payload.get("action")
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
                            str(payload.get("decision_by", "local-approver")),
                        )
                    else:
                        response = {"error": f"unknown action: {action}"}
                except Exception as exc:  # pragma: no cover - best effort server
                    response = {"error": str(exc)}
                self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))

        self._http_server = DemoHTTPServer((self.host, self.web_port), DemoHTTPRequestHandler)
        self._socket_server = DemoSocketServer((self.host, self.socket_port), DemoSocketHandler)

        http_thread = threading.Thread(target=self._http_server.serve_forever, daemon=True)
        socket_thread = threading.Thread(target=self._socket_server.serve_forever, daemon=True)
        http_thread.start()
        socket_thread.start()
        self._threads = [http_thread, socket_thread]
        self._audit("approval-node-started", {"web_url": self.web_url, "socket_port": self.socket_port})

    def stop(self) -> None:
        if self._http_server is not None:
            self._http_server.shutdown()
        if self._socket_server is not None:
            self._socket_server.shutdown()


class ApprovalClient:
    def __init__(self, host: str = "127.0.0.1", socket_port: int = 8765, timeout_seconds: float = 2.0):
        self.host = host
        self.socket_port = socket_port
        self.timeout_seconds = timeout_seconds

    def _send(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with socket.create_connection((self.host, self.socket_port), timeout=self.timeout_seconds) as connection:
            connection.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            response = connection.makefile("r", encoding="utf-8").readline()
        if not response:
            raise RuntimeError("empty response from approval node")
        return json.loads(response)

    def submit_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._send({"action": "submit", "payload": payload})

    def get_status(self, request_id: str) -> Dict[str, Any]:
        return self._send({"action": "status", "request_id": request_id})

    def wait_for_ack(self, request_id: str, timeout_seconds: float = 30.0, poll_interval_seconds: float = 0.5) -> Dict[str, Any]:
        deadline = time.time() + timeout_seconds
        last_status: Dict[str, Any] = {"status": "pending"}
        while time.time() < deadline:
            last_status = self.get_status(request_id)
            if last_status.get("status") in {"approved", "rejected"}:
                return last_status
            time.sleep(poll_interval_seconds)
        return last_status
