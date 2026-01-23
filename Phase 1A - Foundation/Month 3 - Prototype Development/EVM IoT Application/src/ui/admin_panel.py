"""
Admin ECI Panel for VoteGuard Pro EVM
Language: Python (PyQt5)
Allows editing party/candidate metadata, images, and logos.
Persists to data/candidates.json consumed by Voting UI.
"""

import json
import os
from pathlib import Path
from typing import Dict, List

from PyQt5 import QtCore, QtGui, QtWidgets


def candidates_path() -> Path:
    base = Path(__file__).resolve().parents[3]
    return base / "data" / "candidates.json"


def load_candidates() -> List[Dict]:
    fp = candidates_path()
    if not fp.exists():
        return []
    try:
        with fp.open("r", encoding="utf-8") as f:
            data = json.load(f)
            # Support either {"candidates": [...]} or plain list
            if isinstance(data, dict):
                return list(data.get("candidates", []))
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_candidates(items: List[Dict]) -> None:
    fp = candidates_path()
    fp.parent.mkdir(parents=True, exist_ok=True)
    payload = {"candidates": items}
    with fp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


class AdminPanel(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("ECI Admin Panel — Candidates")
        self.resize(900, 600)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [
                "Party",
                "Candidate",
                "Symbol",
                "Image Path",
                "Logo Path",
                "Enabled",
            ]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Controls
        btn_add = QtWidgets.QPushButton("Add")
        btn_edit = QtWidgets.QPushButton("Edit")
        btn_remove = QtWidgets.QPushButton("Remove")
        btn_save = QtWidgets.QPushButton("Save Changes")
        btn_import_logo = QtWidgets.QPushButton("Import Logo…")
        btn_import_image = QtWidgets.QPushButton("Import Image…")

        btn_add.clicked.connect(self._add_entry)
        btn_edit.clicked.connect(self._edit_entry)
        btn_remove.clicked.connect(self._remove_entry)
        btn_save.clicked.connect(self._save_all)
        btn_import_logo.clicked.connect(lambda: self._import_asset(kind="logo"))
        btn_import_image.clicked.connect(lambda: self._import_asset(kind="image"))

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        row = QtWidgets.QHBoxLayout()
        for w in (
            btn_add,
            btn_edit,
            btn_remove,
            btn_import_image,
            btn_import_logo,
            btn_save,
        ):
            row.addWidget(w)
        layout.addLayout(row)

        # Load data
        self._items: List[Dict] = load_candidates()
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(len(self._items))
        for r, item in enumerate(self._items):
            self.table.setItem(r, 0, QtWidgets.QTableWidgetItem(item.get("party", "")))
            self.table.setItem(
                r, 1, QtWidgets.QTableWidgetItem(item.get("candidate", ""))
            )
            self.table.setItem(r, 2, QtWidgets.QTableWidgetItem(item.get("symbol", "")))
            self.table.setItem(
                r, 3, QtWidgets.QTableWidgetItem(item.get("image_path", ""))
            )
            self.table.setItem(
                r, 4, QtWidgets.QTableWidgetItem(item.get("logo_path", ""))
            )
            enabled_item = QtWidgets.QTableWidgetItem(
                "Yes" if item.get("enabled", True) else "No"
            )
            enabled_item.setFlags(enabled_item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table.setItem(r, 5, enabled_item)

    def _add_entry(self):
        dlg = CandidateEditDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self._items.append(dlg.result_item())
            self._refresh_table()

    def _remove_entry(self):
        r = self.table.currentRow()
        if r < 0:
            return
        del self._items[r]
        self._refresh_table()

    def _edit_entry(self):
        r = self.table.currentRow()
        if r < 0:
            return
        dlg = CandidateEditDialog(self, self._items[r])
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self._items[r] = dlg.result_item()
            self._refresh_table()

    def _save_all(self):
        save_candidates(self._items)
        QtWidgets.QMessageBox.information(self, "Saved", "Candidate list saved.")

    def _import_asset(self, kind: str):
        if kind not in {"logo", "image"}:
            return
        r = self.table.currentRow()
        if r < 0:
            return
        fp, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            f"Select {kind} file",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not fp:
            return
        key = "logo_path" if kind == "logo" else "image_path"
        self._items[r][key] = fp
        self._refresh_table()


class CandidateEditDialog(QtWidgets.QDialog):
    def __init__(
        self, parent: QtWidgets.QWidget | None = None, item: Dict | None = None
    ):
        super().__init__(parent)
        self.setWindowTitle("Edit Candidate")
        self.resize(480, 320)
        self._item = item or {}

        self.party_edit = QtWidgets.QLineEdit(self._item.get("party", ""))
        self.candidate_edit = QtWidgets.QLineEdit(self._item.get("candidate", ""))
        self.symbol_edit = QtWidgets.QLineEdit(self._item.get("symbol", ""))
        self.image_edit = QtWidgets.QLineEdit(self._item.get("image_path", ""))
        self.logo_edit = QtWidgets.QLineEdit(self._item.get("logo_path", ""))
        self.enabled_check = QtWidgets.QCheckBox("Enabled")
        self.enabled_check.setChecked(bool(self._item.get("enabled", True)))

        btn_img = QtWidgets.QPushButton("Browse…")
        btn_logo = QtWidgets.QPushButton("Browse…")
        btn_img.clicked.connect(lambda: self._browse_into(self.image_edit))
        btn_logo.clicked.connect(lambda: self._browse_into(self.logo_edit))

        form = QtWidgets.QFormLayout()
        form.addRow("Party", self.party_edit)
        form.addRow("Candidate", self.candidate_edit)
        form.addRow("Symbol", self.symbol_edit)
        img_row = QtWidgets.QHBoxLayout()
        img_row.addWidget(self.image_edit)
        img_row.addWidget(btn_img)
        logo_row = QtWidgets.QHBoxLayout()
        logo_row.addWidget(self.logo_edit)
        logo_row.addWidget(btn_logo)
        form.addRow("Image Path", self._wrap(img_row))
        form.addRow("Logo Path", self._wrap(logo_row))
        form.addRow("Status", self.enabled_check)

        btn_ok = QtWidgets.QPushButton("OK")
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        box = QtWidgets.QHBoxLayout()
        box.addStretch(1)
        box.addWidget(btn_ok)
        box.addWidget(btn_cancel)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(box)

    def _wrap(self, inner: QtWidgets.QLayout) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        w.setLayout(inner)
        return w

    def _browse_into(self, target_edit: QtWidgets.QLineEdit):
        fp, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Image", str(Path.home()), "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if fp:
            target_edit.setText(fp)

    def result_item(self) -> Dict:
        return {
            "party": self.party_edit.text().strip(),
            "candidate": self.candidate_edit.text().strip(),
            "symbol": self.symbol_edit.text().strip(),
            "image_path": self.image_edit.text().strip(),
            "logo_path": self.logo_edit.text().strip(),
            "enabled": self.enabled_check.isChecked(),
        }


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dlg = AdminPanel()
    dlg.show()
    app.exec_()
