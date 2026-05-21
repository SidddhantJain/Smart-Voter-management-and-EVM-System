from __future__ import annotations

import argparse
from threading import Thread

from voteguard.demo.workflow_server import DemoWorkflowServer


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the VoteGuard demo workflow server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--approval-host", default="127.0.0.1")
    parser.add_argument("--approval-port", type=int, default=8765)
    args = parser.parse_args()

    server = DemoWorkflowServer(
        approval_host=args.approval_host,
        approval_port=args.approval_port,
        host=args.host,
        port=args.port,
    )
    print(f"[demo] primary workflow running at http://{args.host}:{args.port}")
    print(f"[demo] approval node expected at {args.approval_host}:{args.approval_port}")
    server.start()


if __name__ == "__main__":
    main()
