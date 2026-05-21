import os
import sys
import subprocess
import argparse

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Start demo approval node and workflow in background")
    parser.add_argument("--no-ui", action="store_true", help="Do not launch the PyQt UI (headless) ")
    parser.add_argument("--approval-port", type=int, default=8765)
    parser.add_argument("--workflow-port", type=int, default=5050)
    args = parser.parse_args()

    if not check_and_install_dependencies():
        sys.exit(1)

    demo_processes = (None, None)
    if args.demo:
        demo_processes = start_demo_processes(approval_port=args.approval_port, workflow_port=args.workflow_port)

    run(use_ui=not args.no_ui)
