"""
VoteGuard Pro EVM IoT Application - Main Entry Point
Language: Python 3.11+
Purpose: Orchestrates UI, hardware, blockchain, and security modules for the EVM device
"""

from blockchain.client import BlockchainClient
from hardware.device_manager import DeviceManager
from security.secure_boot import SecureBoot
from ui.touchscreen import TouchscreenUI
from utils.logger import Logger


def main():
    # Initialize secure boot and device attestation
    SecureBoot.verify_integrity()

    # Initialize hardware interfaces (biometrics, camera, GPS, tamper sensors)
    device_manager = DeviceManager()
    device_manager.initialize_all()

    # Initialize blockchain client
    blockchain = BlockchainClient()
    blockchain.connect()

    # Initialize UI
    ui = TouchscreenUI(device_manager, blockchain)
    ui.run()

    # Main event loop (UI handles voting workflow)
    # All logs and audit events are handled by Logger


if __name__ == "__main__":
    main()
