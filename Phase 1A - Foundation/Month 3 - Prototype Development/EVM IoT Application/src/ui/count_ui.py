from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from voteguard.core.counting import tally
from voteguard.config.env import data_dir, key_path
import json
import csv


class CountUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vote Tally")
        self.resize(600, 400)
        layout = QVBoxLayout()
        self.info = QLabel("Tally from encrypted ballot ledger")
        self.info.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info)
        # Filter by election
        self.filter = QComboBox()
        self.filter.addItem("All Elections")
        self.filter.currentIndexChanged.connect(self.apply_filter)
        layout.addWidget(self.filter)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Election", "Choice", "Count"])
        layout.addWidget(self.table)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_counts)
        layout.addWidget(self.refresh_btn)
        # Export buttons
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self.export_json)
        layout.addWidget(self.export_json_btn)
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_csv_btn)
        self.setLayout(layout)
        self._counts = {}
        self.refresh_counts()

    def refresh_counts(self):
        ledger = data_dir() / "ballot_ledger.json"
        key = key_path()
        try:
            counts = tally(ledger, key, verify=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        self._counts = counts
        self.update_filter_options()
        self.apply_filter()

    def update_filter_options(self):
        current = self.filter.currentText()
        self.filter.blockSignals(True)
        self.filter.clear()
        self.filter.addItem("All Elections")
        for election in sorted(self._counts.keys()):
            self.filter.addItem(election)
        # Restore selection if possible
        idx = self.filter.findText(current)
        if idx >= 0:
            self.filter.setCurrentIndex(idx)
        self.filter.blockSignals(False)

    def apply_filter(self):
        selected = self.filter.currentText()
        rows = []
        for election, choices in self._counts.items():
            if selected != "All Elections" and election != selected:
                continue
            for choice, c in sorted(choices.items(), key=lambda kv: (-kv[1], kv[0])):
                rows.append((election, choice, str(c)))
        self.table.setRowCount(len(rows))
        for r, (election, choice, c) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(election))
            self.table.setItem(r, 1, QTableWidgetItem(choice))
            self.table.setItem(r, 2, QTableWidgetItem(c))

    def export_json(self):
        out_path = data_dir() / "results.json"
        try:
            out_path.write_text(json.dumps(self._counts, indent=2))
            QMessageBox.information(self, "Export", f"Saved JSON to {out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_csv(self):
        out_path = data_dir() / "results.csv"
        try:
            with out_path.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Election", "Choice", "Count"])
                for election, choices in self._counts.items():
                    for choice, c in sorted(choices.items(), key=lambda kv: (-kv[1], kv[0])):
                        w.writerow([election, choice, c])
            QMessageBox.information(self, "Export", f"Saved CSV to {out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
