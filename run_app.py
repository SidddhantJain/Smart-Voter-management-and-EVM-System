import os
import sys
import subprocess
import argparse
import socket
import time


# Add src to sys.path for absolute imports
src_path = os.path.join(
    os.path.dirname(__file__),
    "Phase 1A - Foundation",
    "Month 3 - Prototype Development",
    "EVM IoT Application",
    "src",
)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def check_and_install_dependencies():
    """Check for required packages; auto-install if missing in non-interactive mode."""
    required_packages = {
        "PyQt5": "pyqt5==5.15.10",
        "cryptography": "cryptography==41.0.3",
    }

    missing = []
    for package_name, requirement in required_packages.items():
        try:
            __import__(package_name)
        except ModuleNotFoundError:
            missing.append((package_name, requirement))

    if not missing:
        return True

    print("\n" + "=" * 70)
    print("[WARNING] MISSING DEPENDENCIES")
    print("=" * 70)
    print(f"\nThe following required packages are not installed:")
    for pkg_name, _ in missing:
        print(f"  - {pkg_name}")

    print("\n[INFO] SETUP INSTRUCTIONS:")
    print("\n1. Create and activate a virtual environment:")
    print("   PowerShell:")
    print("     python -m venv venv")
    print("     .\\venv\\Scripts\\Activate.ps1")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements-base.txt")
    print("\n3. Re-run the application:")
    print("   python run_app.py --demo")

    print("\n[INFO] Attempting auto-install...")
    print("=" * 70)

    req_file = os.path.join(os.path.dirname(__file__), "requirements-base.txt")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", req_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[OK] Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Installation failed:")
        print(f"   pip install -r requirements-base.txt\n")
        print(f"Error details: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Could not auto-install: {e}")
        print(f"   Please run manually: pip install -r requirements-base.txt")
        return False


def start_demo_processes(approval_port: int = 8765, workflow_port: int = 5050):
    """Start demo approval node and workflow in background subprocesses."""
    base = os.path.dirname(__file__)
    approval_script = os.path.join(base, "run_demo_approval_node.py")
    workflow_script = os.path.join(base, "run_demo_workflow.py")

    # Start approval node
    try:
        p1 = subprocess.Popen([sys.executable, approval_script, "--socket-port", str(approval_port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[demo] started approval node (pid={p1.pid}) on port {approval_port}")
    except Exception as e:
        print(f"[demo] failed to start approval node: {e}")
        p1 = None

    # Start workflow server
    try:
        p2 = subprocess.Popen([sys.executable, workflow_script, "--approval-host", "127.0.0.1", "--approval-port", str(approval_port), "--port", str(workflow_port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[demo] started workflow server (pid={p2.pid}) on port {workflow_port}")
    except Exception as e:
        print(f"[demo] failed to start workflow server: {e}")
        p2 = None

    return p1, p2


def start_verification_server_process(web_port: int = 8085, socket_port: int = 8785):
    """Start the standalone verification server from the server folder."""

    base = os.path.dirname(__file__)
    server_script = os.path.join(base, "server", "run_server.py")

    try:
        process = subprocess.Popen(
            [
                sys.executable,
                server_script,
                "--host",
                "0.0.0.0",
                "--web-port",
                str(web_port),
                "--socket-port",
                str(socket_port),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"[server] started verification server (pid={process.pid}) at 0.0.0.0:{socket_port}")
        return process
    except FileNotFoundError as exc:
        print(f"[server] could not find launcher script: {exc}")
    except Exception as exc:
        print(f"[server] failed to start verification server: {exc}")
    return None


def wait_for_tcp_port(host: str, port: int, timeout_seconds: float = 20.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except Exception:
            time.sleep(0.25)
    return False


def run(use_ui: bool = True):
    """Launch the VoteGuard Pro application."""
    try:
        if use_ui:
            from PyQt5.QtWidgets import QApplication
            from ui.main_ui import MainUI

            app = QApplication([])
            main_ui = MainUI()
            main_ui.show()
            app.exec_()
        else:
            print("[info] UI disabled; nothing to run.")
    except ModuleNotFoundError as e:
        print(f"\n[ERROR] Missing module '{e.name}'")
        print("   Please ensure all dependencies are installed.")
        print("   Run: pip install -r requirements-base.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


def configure_election_settings(args):
    """Persist network settings before the UI loads them."""

    try:
        from voteguard.config.election import save_election_settings
    except Exception as exc:
        print(f"[warning] Could not import election settings helper: {exc}")
        return

    payload = {}
    if args.server_host:
        payload["server_host"] = args.server_host
    if args.server_port:
        payload["server_port"] = args.server_port
    if args.approval_host:
        payload["approval_host"] = args.approval_host
    if args.approval_port:
        payload["approval_port"] = args.approval_port
    if args.election_type:
        payload["election_type"] = args.election_type
    if args.constituency is not None:
        payload["constituency"] = args.constituency
    if args.state is not None:
        payload["state"] = args.state

    if payload:
        path = save_election_settings(payload)
        print(f"[info] Saved election settings to {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Start demo approval node and workflow in background")
    parser.add_argument("--start-server", action="store_true", help="Start the standalone verification server from the server folder")
    parser.add_argument("--no-ui", action="store_true", help="Do not launch the PyQt UI (headless) ")
    parser.add_argument("--approval-port", type=int, default=8765)
    parser.add_argument("--workflow-port", type=int, default=5050)
    parser.add_argument("--server-web-port", type=int, default=int(os.getenv("VOTEGUARD_SERVER_WEB_PORT", "8085")), help="HTTP port for the standalone verification server")
    parser.add_argument("--server-host", default=os.getenv("VOTEGUARD_SERVER_HOST", ""), help="Server host for biometric verification requests")
    parser.add_argument("--server-port", type=int, default=int(os.getenv("VOTEGUARD_SERVER_PORT", "8785")), help="Server port for biometric verification requests")
    parser.add_argument("--approval-host", default=os.getenv("VOTEGUARD_APPROVAL_HOST", ""), help="Approval host for workflow and demo routing")
    parser.add_argument("--election-type", default=os.getenv("VOTEGUARD_ELECTION_TYPE", ""), help="Election type to persist before launch")
    parser.add_argument("--constituency", default=None, help="Constituency to persist before launch")
    parser.add_argument("--state", default=None, help="State to persist before launch")
    args = parser.parse_args()

    if not check_and_install_dependencies():
        sys.exit(1)

    configure_election_settings(args)

    server_process = None
    if args.start_server:
        server_process = start_verification_server_process(
            web_port=args.server_web_port,
            socket_port=args.server_port,
        )
        if server_process is None:
            sys.exit(1)
        if not wait_for_tcp_port("127.0.0.1", args.server_port, timeout_seconds=30.0):
            print(f"[server] verification server did not become ready on port {args.server_port}")
            sys.exit(1)

    if args.start_server and args.no_ui:
        print("[server] server-only mode active; press Ctrl+C to stop.")
        try:
            while server_process is not None and server_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[server] stopping server-only mode")
        finally:
            if server_process is not None and server_process.poll() is None:
                try:
                    server_process.terminate()
                except Exception:
                    pass
        sys.exit(0)

    demo_processes = (None, None)
    if args.demo:
        demo_processes = start_demo_processes(approval_port=args.approval_port, workflow_port=args.workflow_port)

    try:
        run(use_ui=not args.no_ui)
    finally:
        if server_process is not None and server_process.poll() is None:
            try:
                server_process.terminate()
            except Exception:
                pass
