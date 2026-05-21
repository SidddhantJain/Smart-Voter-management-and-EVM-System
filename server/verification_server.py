from __future__ import annotations

import hmac
import html
import json
import secrets
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
class VerificationRecord:
    request_id: str
    session_id: str
    aadhaar_id: str
    voter_id: str
    constituency: str
    election_type: str
    biometric_ok: bool
    face_ok: bool
    device_connected: bool
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    decided_at: Optional[float] = None
    signature: Optional[str] = None
    rejection_reason: Optional[str] = None
    ack_sequence: List[Dict[str, Any]] = field(default_factory=list)
    device_checks: Dict[str, Any] = field(default_factory=dict)


class VerificationServer:
    def __init__(self, host: str = "0.0.0.0", web_port: int = 8085, socket_port: int = 8785, secret: Optional[str] = None):
        self.host = host
        self.web_port = web_port
        self.socket_port = socket_port
        self.secret = secret or secrets.token_hex(24)
        self._lock = threading.Lock()
        self._records: Dict[str, VerificationRecord] = {}
        self._http_server: Optional[ThreadingHTTPServer] = None
        self._socket_server: Optional[socketserver.ThreadingTCPServer] = None

    def _canonical_signature(self, record: VerificationRecord) -> str:
        payload = json.dumps(
            {
                "request_id": record.request_id,
                "status": record.status,
                "session_id": record.session_id,
                "aadhaar_id": record.aadhaar_id,
                "voter_id": record.voter_id,
                "constituency": record.constituency,
                "election_type": record.election_type,
                "decided_at": record.decided_at,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), sha256).hexdigest()

    def _valid_aadhaar(self, aadhaar_id: str) -> bool:
        digits = "".join(ch for ch in aadhaar_id if ch.isdigit())
        return len(digits) == 12

    def _valid_voter_id(self, voter_id: str) -> bool:
        cleaned = voter_id.strip()
        return len(cleaned) >= 6 and any(ch.isalpha() for ch in cleaned) and any(ch.isdigit() for ch in cleaned)

    def _build_device_checks(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "device_connected": bool(payload.get("device_connected", True)),
            "camera_ready": bool(payload.get("camera_ready", True)),
            "biometric_sensor_ready": bool(payload.get("biometric_sensor_ready", True)),
        }

    def _as_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        text = str(value).strip().lower()
        return text in {"1", "true", "yes", "on", "y", "checked"}

    def _build_ack_sequence(self, record: VerificationRecord) -> List[Dict[str, Any]]:
        return [
            {
                "stage": "ack-1",
                "message": "Connection received and request registered.",
                "status": "received",
            },
            {
                "stage": "ack-2",
                "message": "Aadhaar, voter id, and device readiness checked.",
                "status": "checked",
            },
            {
                "stage": "ack-3",
                "message": "Biometric / face verification gated for approval.",
                "status": "approved" if record.status == "approved" else "rejected",
            },
        ]

    def submit_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request_id = secrets.token_hex(8)
        session_id = str(payload.get("session_id", ""))
        aadhaar_id = str(payload.get("aadhaar_id", ""))
        voter_id = str(payload.get("voter_id", ""))
        constituency = str(payload.get("constituency", ""))
        election_type = str(payload.get("election_type", ""))
        biometric_ok = self._as_bool(payload.get("biometric_ok", False))
        face_ok = self._as_bool(payload.get("face_ok", False))
        device_checks = self._build_device_checks(payload)

        approved = all(
            [
                device_checks["device_connected"],
                device_checks["camera_ready"],
                device_checks["biometric_sensor_ready"],
                self._valid_aadhaar(aadhaar_id),
                self._valid_voter_id(voter_id),
                biometric_ok,
                face_ok,
            ]
        )

        record = VerificationRecord(
            request_id=request_id,
            session_id=session_id,
            aadhaar_id=aadhaar_id,
            voter_id=voter_id,
            constituency=constituency,
            election_type=election_type,
            biometric_ok=biometric_ok,
            face_ok=face_ok,
            device_connected=bool(device_checks["device_connected"]),
            status="approved" if approved else "rejected",
            decided_at=time.time(),
            rejection_reason=None if approved else "One or more verification checks failed.",
            device_checks=device_checks,
        )
        record.signature = self._canonical_signature(record)
        record.ack_sequence = self._build_ack_sequence(record)
        with self._lock:
            self._records[request_id] = record
        return self._record_to_dict(record)

    def get_status(self, request_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._record_to_dict(self._records[request_id])

    def list_requests(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self._record_to_dict(record) for record in self._records.values()]

    def _record_to_dict(self, record: VerificationRecord) -> Dict[str, Any]:
        return {
            "request_id": record.request_id,
            "session_id": record.session_id,
            "aadhaar_id": record.aadhaar_id,
            "voter_id": record.voter_id,
            "constituency": record.constituency,
            "election_type": record.election_type,
            "biometric_ok": record.biometric_ok,
            "face_ok": record.face_ok,
            "device_connected": record.device_connected,
            "status": record.status,
            "created_at": record.created_at,
            "decided_at": record.decided_at,
            "signature": record.signature,
            "rejection_reason": record.rejection_reason,
            "ack_sequence": record.ack_sequence,
            "device_checks": record.device_checks,
        }

    def render_dashboard(self) -> str:
        cards = []
        for record in sorted(self.list_requests(), key=lambda item: item["created_at"], reverse=True):
            ack_html = "".join(
                f"<li><strong>{html.escape(item['stage'])}</strong>: {html.escape(item['message'])}</li>"
                for item in record.get("ack_sequence", [])
            )
            cards.append(
                f"""
                <div class="request-card {record['status']}">
                  <div class="request-header">
                    <span class="badge">{html.escape(record['status']).upper()}</span>
                    <strong>{html.escape(record['aadhaar_id'] or 'No Aadhaar')}</strong>
                  </div>
                  <div class="request-body">
                    <div><span>Request ID</span><code>{html.escape(record['request_id'])}</code></div>
                    <div><span>Voter ID</span><code>{html.escape(record['voter_id'])}</code></div>
                    <div><span>Constituency</span>{html.escape(record['constituency'] or '-')}</div>
                    <div><span>Election</span>{html.escape(record['election_type'] or '-')}</div>
                    <div><span>Signature</span>{html.escape(record['signature'] or 'pending')}</div>
                    <div><span>Checks</span>{html.escape(json.dumps(record.get('device_checks', {})))}</div>
                    <div><span>Acknowledgments</span><ul>{ack_html}</ul></div>
                  </div>
                </div>
                """
            )
        cards_html = ''.join(cards) if cards else '<div class="request-card"><strong>No verification requests yet.</strong></div>'
        return f"""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta http-equiv="refresh" content="2">
          <title>VoteGuard Verification Server</title>
          <style>
            body {{ margin: 0; font-family: Arial, sans-serif; background: linear-gradient(180deg, #10243f, #07101b); color: #eaf3ff; }}
            .wrap {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
            .hero {{ display:flex; justify-content:space-between; gap: 16px; align-items:center; margin-bottom: 20px; }}
            .title {{ font-size: 30px; font-weight: 800; }}
            .subtitle {{ opacity: .8; max-width: 720px; line-height: 1.5; }}
            .banner {{ background: rgba(67,217,163,.14); border: 1px solid rgba(67,217,163,.35); padding: 12px 16px; border-radius: 14px; }}
            .grid {{ display:grid; grid-template-columns: 1.7fr 1fr; gap: 18px; }}
            .panel {{ background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); border-radius: 18px; padding: 18px; }}
            .request-card {{ padding: 14px; border-radius: 16px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); margin-bottom: 12px; }}
            .request-card.approved {{ border-color: rgba(67,217,163,.5); }}
            .request-card.rejected {{ border-color: rgba(255,107,107,.5); }}
            .badge {{ display:inline-block; font-size: 12px; letter-spacing: .14em; padding: 4px 8px; border-radius: 999px; background: rgba(255,255,255,.08); margin-right: 10px; }}
            .request-body {{ display:grid; gap: 8px; margin-top: 10px; }}
            .request-body span {{ display:inline-block; width: 110px; color: #8ca6c9; }}
            code {{ background: rgba(0,0,0,.25); padding: 2px 6px; border-radius: 8px; }}
            ul {{ margin: 0; padding-left: 18px; line-height: 1.5; }}
            .footer {{ margin-top: 16px; opacity: .75; font-size: 13px; }}
            input, select, button {{ font-size: 14px; }}
            form {{ display:grid; gap: 10px; margin-top: 8px; }}
            label {{ display:grid; gap: 6px; }}
            .row {{ display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            button {{ border: 0; border-radius: 12px; padding: 10px 14px; font-weight: 700; cursor: pointer; background: #43d9a3; color: #071d14; }}
          </style>
        </head>
        <body>
          <div class="wrap">
            <div class="hero">
              <div>
                <div class="title">VoteGuard Verification Server</div>
                <div class="subtitle">Server-side verification gate for biometric, face, Aadhaar, voter ID, and device readiness checks. When all checks pass, a signed approval is issued for forwarding.</div>
              </div>
              <div class="banner">3-way acknowledgment • Signed approval • Device health checks</div>
            </div>
            <div class="grid">
              <div class="panel">
                <h3>Verification Requests</h3>
                {cards_html}
              </div>
              <div class="panel">
                <h3>Manual Submit</h3>
                <form method="post" action="/api/submit">
                  <label>Session ID<input name="session_id"></label>
                  <div class="row">
                    <label>Aadhaar ID<input name="aadhaar_id"></label>
                    <label>Voter ID<input name="voter_id"></label>
                  </div>
                  <label>Constituency<input name="constituency"></label>
                  <label>Election Type<input name="election_type" placeholder="Vidhan Sabha"></label>
                  <div class="row">
                    <label>Biometric OK<input name="biometric_ok" value="1"></label>
                    <label>Face OK<input name="face_ok" value="1"></label>
                  </div>
                  <button type="submit">Submit Verification</button>
                </form>
              </div>
            </div>
            <div class="footer">The server treats missing connectivity or invalid IDs as rejection reasons. It is intended for local transfer and demonstration only.</div>
          </div>
        </body>
        </html>
        """

    def start(self) -> None:
        server = self

        class HTTPHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover
                return

            def _send_html(self, text: str, status: int = 200) -> None:
                payload = text.encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
                data = json.dumps(payload, indent=2).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path in {"/", "/index.html"}:
                    self._send_html(server.render_dashboard())
                    return
                if parsed.path == "/api/requests":
                    self._send_json({"requests": server.list_requests()})
                    return
                if parsed.path == "/api/request":
                    params = parse_qs(parsed.query)
                    request_id = params.get("request_id", [""])[0]
                    if not request_id:
                        self._send_json({"error": "request_id is required"}, status=HTTPStatus.BAD_REQUEST)
                        return
                    try:
                        self._send_json(server.get_status(request_id))
                    except KeyError:
                        self._send_json({"error": "unknown request"}, status=HTTPStatus.NOT_FOUND)
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length).decode("utf-8")
                if parsed.path == "/api/submit":
                    fields = parse_qs(body)
                    payload = {
                        "session_id": fields.get("session_id", [""])[0],
                        "aadhaar_id": fields.get("aadhaar_id", [""])[0],
                        "voter_id": fields.get("voter_id", [""])[0],
                        "constituency": fields.get("constituency", [""])[0],
                        "election_type": fields.get("election_type", [""])[0],
                        "biometric_ok": fields.get("biometric_ok", [""])[0],
                        "face_ok": fields.get("face_ok", [""])[0],
                        "device_connected": True,
                        "camera_ready": True,
                        "biometric_sensor_ready": True,
                    }
                    result = server.submit_request(payload)
                    self._send_html(f"<pre>{html.escape(json.dumps(result, indent=2))}</pre>")
                    return
                self.send_error(HTTPStatus.NOT_FOUND)

        class TCPHandler(socketserver.StreamRequestHandler):
            def handle(self) -> None:
                raw = self.rfile.readline().decode("utf-8").strip()
                if not raw:
                    return
                try:
                    payload = json.loads(raw)
                    action = payload.get("action")
                    if action == "submit":
                        response = server.submit_request(payload.get("payload", {}))
                    elif action == "status":
                        response = server.get_status(str(payload.get("request_id", "")))
                    elif action == "list":
                        response = {"requests": server.list_requests()}
                    else:
                        response = {"error": f"unknown action: {action}"}
                except Exception as exc:
                    response = {"error": str(exc)}
                self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))

        class ReusableHTTPServer(ThreadingHTTPServer):
            allow_reuse_address = True

        class ReusableTCPServer(socketserver.ThreadingTCPServer):
            allow_reuse_address = True

        self._http_server = ReusableHTTPServer((self.host, self.web_port), HTTPHandler)
        self._socket_server = ReusableTCPServer((self.host, self.socket_port), TCPHandler)

        threading.Thread(target=self._http_server.serve_forever, daemon=True).start()
        threading.Thread(target=self._socket_server.serve_forever, daemon=True).start()

    def stop(self) -> None:
        if self._http_server is not None:
            self._http_server.shutdown()
        if self._socket_server is not None:
            self._socket_server.shutdown()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the VoteGuard verification server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--web-port", type=int, default=8085)
    parser.add_argument("--socket-port", type=int, default=8785)
    args = parser.parse_args()

    server = VerificationServer(host=args.host, web_port=args.web_port, socket_port=args.socket_port)
    server.start()
    print(f"[VerificationServer] HTTP: http://{args.host}:{args.web_port}")
    print(f"[VerificationServer] TCP: {args.host}:{args.socket_port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
