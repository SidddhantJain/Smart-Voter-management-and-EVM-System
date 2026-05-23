import sys
import subprocess
from pathlib import Path

# Ensure workspace root is on sys.path for package imports
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def check_and_install_dependencies():
    """Check for required packages; auto-install if missing in non-interactive mode."""
    required_packages = {
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
    print("\n3. Re-run the tally script:")
    print("   python run_tally.py")
    
    print("\n[INFO] Attempting auto-install...")
    print("=" * 70)
    
    req_file = ROOT / "requirements-base.txt"
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
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


def main() -> int:
    """Run the vote tally process."""
    try:
        from voteguard.config.env import data_dir, key_path
        from voteguard.core.counting import tally
        
        ledger = data_dir() / "ballot_ledger.json"
        key = key_path()
        try:
            counts = tally(ledger, key, verify=True)
        except Exception as e:
            print(f"ERROR: {e}")
            return 1

        print("Vote Tally:")
        for election, choices in counts.items():
            print(f"- {election}")
            for choice, c in sorted(choices.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"  * {choice}: {c}")
        return 0
    except ModuleNotFoundError as e:
        print(f"\n[ERROR] Missing module '{e.name}'")
        print("   Please ensure all dependencies are installed.")
        print("   Run: pip install -r requirements-base.txt")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    if not check_and_install_dependencies():
        sys.exit(1)
    sys.exit(main())
