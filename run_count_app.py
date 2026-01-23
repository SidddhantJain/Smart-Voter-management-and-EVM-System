import sys
import os
from PyQt5.QtWidgets import QApplication

# Add src to sys.path for absolute imports
src_path = os.path.join(os.path.dirname(__file__), 'Phase 1A - Foundation', 'Month 3 - Prototype Development', 'EVM IoT Application', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ui.count_ui import CountUI


def run():
    app = QApplication([])
    ui = CountUI()
    ui.show()
    app.exec_()


if __name__ == "__main__":
    run()
