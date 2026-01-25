import csv
import json
from pathlib import Path

import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from scripts.verify_ledger import verify as verify_ledger
from voteguard.config.env import data_dir, key_path
from voteguard.core.counting import tally


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
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Election", "Choice", "Count", "%"])
        layout.addWidget(self.table)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_counts)
        layout.addWidget(self.refresh_btn)
        # Auto-refresh controls
        auto_row = QHBoxLayout()
        self.auto_refresh_chk = QCheckBox("Auto-Refresh")
        self.auto_refresh_chk.stateChanged.connect(self.toggle_auto_refresh)
        auto_row.addWidget(self.auto_refresh_chk)
        auto_row.addWidget(QLabel("Interval (s):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 300)
        self.interval_spin.setValue(10)
        self.interval_spin.valueChanged.connect(self.update_timer_interval)
        auto_row.addWidget(self.interval_spin)
        layout.addLayout(auto_row)
        # Export buttons
        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.clicked.connect(self.export_json)
        layout.addWidget(self.export_json_btn)
        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_csv_btn)
        # Export filtered buttons
        self.export_json_filtered_btn = QPushButton("Export Filtered JSON")
        self.export_json_filtered_btn.clicked.connect(self.export_json_filtered)
        layout.addWidget(self.export_json_filtered_btn)
        self.export_csv_filtered_btn = QPushButton("Export Filtered CSV")
        self.export_csv_filtered_btn.clicked.connect(self.export_csv_filtered)
        layout.addWidget(self.export_csv_filtered_btn)
        # Status bar label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        # Chart area
        # Enable antialiasing to reduce visual jitter on Windows
        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget()
        self.plot.setBackground("w")
        # Disable mouse panning/zoom to avoid accidental reflows
        self.plot.setMouseEnabled(x=False, y=False)
        layout.addWidget(self.plot)
        self.setLayout(layout)
        self._counts = {}
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_counts)
        # Cached bar graph item to update without clearing (reduces flicker)
        self._bar_item = None
        self.update_timer_interval()
        self.refresh_counts()

    def refresh_counts(self):
        ledger = data_dir() / "ballot_ledger.json"
        key = key_path()
        try:
            counts = tally(ledger, key, verify=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        # Update integrity status
        code = verify_ledger(ledger)
        integrity = "OK" if code == 0 else "FAIL"
        from datetime import datetime

        self.status_label.setText(
            f"Last refresh: {datetime.now().strftime('%H:%M:%S')} | Integrity: {integrity} | Records: {sum(len(v) for v in counts.values())}"
        )
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
        totals: dict[str, int] = {}
        for election, choices in self._counts.items():
            if selected != "All Elections" and election != selected:
                continue
            for choice, c in sorted(choices.items(), key=lambda kv: (-kv[1], kv[0])):
                rows.append((election, choice, c))
                totals[election] = totals.get(election, 0) + c
        # Add totals row(s)
        for election, total in totals.items():
            rows.append((election, "TOTAL", total))
        self.table.setRowCount(len(rows))
        for r, (election, choice, c) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(election))
            self.table.setItem(r, 1, QTableWidgetItem(choice))
            self.table.setItem(r, 2, QTableWidgetItem(str(c)))
            # Percentage based on per-election total
            total_for_election = totals.get(election, 0)
            pct = (
                100.0
                if choice == "TOTAL" and total_for_election
                else (100.0 * (c / total_for_election) if total_for_election else 0.0)
            )
            self.table.setItem(r, 3, QTableWidgetItem(f"{pct:.1f}%"))
        # Draw chart for selected
        self.draw_chart(selected, totals)

    def draw_chart(self, selected: str, totals: dict):
        if selected == "All Elections":
            labels = list(totals.keys())
            values = [totals[e] for e in labels]
            x = list(range(len(labels)))
            if self._bar_item and getattr(self._bar_item, "_labels_len", None) == len(labels):
                # Update heights in-place to avoid tearing
                self._bar_item.setOpts(height=values, x=x)
            else:
                if self._bar_item:
                    self.plot.removeItem(self._bar_item)
                self._bar_item = pg.BarGraphItem(
                    x=x, height=values, width=0.6, brush=pg.mkBrush("#5c6bc0")
                )
                self._bar_item._labels_len = len(labels)
                self.plot.addItem(self._bar_item)
            self.plot.getPlotItem().setTitle("Votes per Election")
            self.plot.getPlotItem().getAxis("bottom").setTicks([list(zip(x, labels))])
        else:
            choices = self._counts.get(selected, {})
            labels = list(choices.keys())
            values = [choices[c] for c in labels]
            x = list(range(len(labels)))
            if self._bar_item and getattr(self._bar_item, "_labels_len", None) == len(labels):
                self._bar_item.setOpts(height=values, x=x, brush=pg.mkBrush("#26a69a"))
            else:
                if self._bar_item:
                    self.plot.removeItem(self._bar_item)
                self._bar_item = pg.BarGraphItem(
                    x=x, height=values, width=0.6, brush=pg.mkBrush("#26a69a")
                )
                self._bar_item._labels_len = len(labels)
                self.plot.addItem(self._bar_item)
            self.plot.getPlotItem().setTitle(f"{selected} — Votes per Choice")
            self.plot.getPlotItem().getAxis("bottom").setTicks([list(zip(x, labels))])
        self.plot.getPlotItem().getAxis("left").setLabel(text="Count")

    def export_json(self):
        suggested = str((data_dir() / "results.json").resolve())
        path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON", suggested, "JSON Files (*.json);;All Files (*.*)"
        )
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(self._counts, indent=2))
            QMessageBox.information(self, "Export", f"Saved JSON to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_csv(self):
        suggested = str((data_dir() / "results.csv").resolve())
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", suggested, "CSV Files (*.csv);;All Files (*.*)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Election", "Choice", "Count"])
                for election, choices in self._counts.items():
                    for choice, c in sorted(
                        choices.items(), key=lambda kv: (-kv[1], kv[0])
                    ):
                        w.writerow([election, choice, c])
            QMessageBox.information(self, "Export", f"Saved CSV to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_json_filtered(self):
        selected = self.filter.currentText()
        suggested_name = (
            "results_filtered.json"
            if selected == "All Elections"
            else f"results_{selected}.json"
        )
        suggested = str((data_dir() / suggested_name).resolve())
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Filtered JSON",
            suggested,
            "JSON Files (*.json);;All Files (*.*)",
        )
        if not path:
            return
        try:
            data = self._filtered_counts(selected)
            Path(path).write_text(json.dumps(data, indent=2))
            QMessageBox.information(self, "Export", f"Saved JSON to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_csv_filtered(self):
        selected = self.filter.currentText()
        suggested_name = (
            "results_filtered.csv"
            if selected == "All Elections"
            else f"results_{selected}.csv"
        )
        suggested = str((data_dir() / suggested_name).resolve())
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Filtered CSV", suggested, "CSV Files (*.csv);;All Files (*.*)"
        )
        if not path:
            return
        try:
            data = self._filtered_counts(selected)
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Election", "Choice", "Count"])
                for election, choices in data.items():
                    for choice, c in sorted(
                        choices.items(), key=lambda kv: (-kv[1], kv[0])
                    ):
                        w.writerow([election, choice, c])
            QMessageBox.information(self, "Export", f"Saved CSV to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _filtered_counts(self, selected: str):
        if selected == "All Elections":
            return self._counts
        else:
            return {selected: self._counts.get(selected, {})}

    def toggle_auto_refresh(self):
        if self.auto_refresh_chk.isChecked():
            self._timer.start(self.interval_spin.value() * 1000)
        else:
            self._timer.stop()

    def update_timer_interval(self):
        if self._timer.isActive():
            self._timer.start(self.interval_spin.value() * 1000)
