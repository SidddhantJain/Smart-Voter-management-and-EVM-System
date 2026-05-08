import os
import sys
import subprocess

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
    print("   python run_count_app.py")
    
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


def run():
    """Launch the VoteGuard Pro Counting application."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.count_ui import CountUI
        
        app = QApplication([])
        ui = CountUI()
        ui.show()
        app.exec_()
    except ModuleNotFoundError as e:
        print(f"\n[ERROR] Missing module '{e.name}'")
        print("   Please ensure all dependencies are installed.")
        print("   Run: pip install -r requirements-base.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if not check_and_install_dependencies():
        sys.exit(1)
    run()
