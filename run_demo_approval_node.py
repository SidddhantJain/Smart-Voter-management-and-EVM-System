from __future__ import annotations

import argparse
import threading
import time

from voteguard.demo.approval_node import MockApprovalNode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the VoteGuard demo approval node")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--web-port", type=int, default=8081)
    parser.add_argument("--socket-port", type=int, default=8765)
    args = parser.parse_args()

    node = MockApprovalNode(host=args.host, web_port=args.web_port, socket_port=args.socket_port)
    node.start()
    print(f"[demo] approval node web UI: {node.web_url}")
    print(f"[demo] approval node socket listener: {args.host}:{args.socket_port}")
    print("[demo] press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        node.stop()


if __name__ == "__main__":
    main()
