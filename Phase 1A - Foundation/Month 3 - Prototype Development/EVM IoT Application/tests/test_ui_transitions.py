import os
import sys
import unittest

# Ensure src is importable
SRC_PATH = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, os.path.abspath(SRC_PATH))

from PyQt5.QtWidgets import QApplication
from ui.main_ui import MainUI


class TestUITransitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()

    def test_stack_initialization_and_switch(self):
        ui = MainUI()
        # Stacked screens: Aadhaar (index 0), Biometric (index 1)
        self.assertGreaterEqual(ui.count(), 2)
        self.assertEqual(ui.currentIndex(), 0)
        # Switch to Biometric
        ui.setCurrentIndex(1)
        self.assertEqual(ui.currentIndex(), 1)


if __name__ == '__main__':
    unittest.main()
