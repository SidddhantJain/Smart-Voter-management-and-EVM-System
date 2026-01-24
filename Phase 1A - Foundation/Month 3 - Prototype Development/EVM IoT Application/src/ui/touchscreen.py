"""
Touchscreen UI for VoteGuard Pro EVM
Language: Python (PyQt5/Kivy placeholder)
Handles: Voter authentication, ballot selection, vote confirmation
"""

from utils.logger import Logger


class TouchscreenUI:
    def __init__(self, device_manager, blockchain_client):
        self.device_manager = device_manager
        self.blockchain_client = blockchain_client

    def run(self):
        print("[UI] Touchscreen interface started.")
        print("[UI] Capturing biometrics and camera image...")
        capture_results = self.device_manager.capture_all()
        Logger.log(f"Biometric and camera capture: {capture_results}")

        # Simulate authentication and voting
        if all(capture_results.values()):
            print("[UI] Authentication successful. Proceeding to ballot selection...")
            Logger.log("Authentication successful.")
            # Placeholder: Simulate ballot selection
            selected_candidate = "Candidate_A"
            print(f"[UI] Voter selected: {selected_candidate}")
            Logger.log(f"Voter selected: {selected_candidate}")
            # Submit vote to blockchain
            tx_result = self.blockchain_client.submit_vote(selected_candidate)
            print(f"[UI] Vote submitted. Blockchain result: {tx_result}")
            Logger.log(f"Vote submitted. Blockchain result: {tx_result}")
        else:
            print("[UI] Authentication failed. Access denied.")
            Logger.log("Authentication failed. Access denied.")
