import os
import sys

# Add src to sys.path for absolute imports
src_path = os.path.join(
    os.path.dirname(__file__),
    "Phase 1A - Foundation",
    "Month 3 - Prototype Development",
    "EVM IoT Application",
    "src",
)
sys.path.insert(0, src_path)

from ui.main_ui import main

if __name__ == "__main__":
    main()
