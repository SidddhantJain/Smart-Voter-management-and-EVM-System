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
from voteguard.config.env import data_dir

try:
    # Optional IPFS helper; admin tools will degrade gracefully
    # when IPFS is not available.
    from backend import ipfs_client  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    ipfs_client = None  # type: ignore


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
        # Hardware/device actions for admin
        btn_check_devices = QtWidgets.QPushButton("Check Devices")
        btn_test_devices = QtWidgets.QPushButton("Test Devices")
        # IPFS / audit tools
        btn_show_ipfs = QtWidgets.QPushButton("Show Recent IPFS CIDs")
        btn_verify_ipfs = QtWidgets.QPushButton("Verify IPFS CID…")

        btn_add.clicked.connect(self._add_entry)
        btn_edit.clicked.connect(self._edit_entry)
        btn_remove.clicked.connect(self._remove_entry)
        btn_save.clicked.connect(self._save_all)
        btn_import_logo.clicked.connect(lambda: self._import_asset(kind="logo"))
        btn_import_image.clicked.connect(lambda: self._import_asset(kind="image"))
        btn_check_devices.clicked.connect(self._check_devices)
        btn_test_devices.clicked.connect(self._test_devices)
        btn_show_ipfs.clicked.connect(self._show_recent_ipfs)
        btn_verify_ipfs.clicked.connect(self._verify_ipfs_cid)

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
            btn_check_devices,
            btn_test_devices,
            btn_show_ipfs,
            btn_verify_ipfs,
            btn_save,
        ):
            row.addWidget(w)
        layout.addLayout(row)

        # Load data
        self._items: List[Dict] = load_candidates()
        self._refresh_table()

    # --- IPFS / audit tools ------------------------------------------------------

    def _read_audit_records(self) -> List[Dict]:
        """Load raw audit records from the hash-chained audit ledger.

        Returns a list of dicts with at least 'kind' and 'details'.
        Any error yields an empty list.
        """

        try:
            path = data_dir() / "audit_ledger.json"
            if not path.exists():
                return []
            data = json.loads(path.read_text("utf-8"))
            return data.get("records", [])
        except Exception:
            return []

    def _show_recent_ipfs(self) -> None:
        """Show the last N IPFS-related CIDs from the audit ledger.

        This scans audit_ledger.json for events that include an
        'ipfs_cid' in their payload and shows a concise list for
        quick reference by the administrator.
        """

        records = self._read_audit_records()
        if not records:
            QtWidgets.QMessageBox.information(
                self,
                "IPFS CIDs",
                "No audit records found yet.",
            )
            return

        # Newest first (records are stored in append order)
        recent = []
        for rec in reversed(records):
            try:
                payload = json.loads(rec.get("payload", "{}"))
            except Exception:
                continue
            details = payload.get("details", {})
            cid = details.get("ipfs_cid")
            if not cid:
                continue
            recent.append(
                {
                    "seq": rec.get("seq"),
                    "kind": payload.get("kind"),
                    "cid": cid,
                }
            )
            if len(recent) >= 10:
                break

        if not recent:
            QtWidgets.QMessageBox.information(
                self,
                "IPFS CIDs",
                "No IPFS CIDs found in audit records yet.",
            )
            return

        lines = ["Last IPFS-related CIDs (newest first):", ""]
        for r in recent:
            lines.append(
                f"Seq {r['seq']}: {r['kind']}\n  CID: {r['cid']}"
            )
        QtWidgets.QMessageBox.information(
            self,
            "IPFS CIDs",
            "\n".join(lines),
        )

    def _verify_ipfs_cid(self) -> None:
        """Verify that a CID's content matches current results or audit files.

        This prompts the admin for a CID and then compares the IPFS
        content to the on-disk results.json and audit_ledger.json
        (if present). It reports whether each comparison matches.
        """

        if ipfs_client is None or not getattr(ipfs_client, "cat", None):
            QtWidgets.QMessageBox.warning(
                self,
                "IPFS Verify",
                "IPFS client is not available in this environment.",
            )
            return

        cid, ok = QtWidgets.QInputDialog.getText(
            self,
            "Verify IPFS CID",
            "Enter IPFS CID to verify:",
        )
        if not ok or not cid.strip():
            return
        cid = cid.strip()

        data = ipfs_client.cat(cid)
        if data is None:
            QtWidgets.QMessageBox.warning(
                self,
                "IPFS Verify",
                "Could not fetch content for this CID from IPFS.",
            )
            return

        results_path = (data_dir() / "results.json").resolve()
        audit_path = (data_dir() / "audit_ledger.json").resolve()

        def load_bytes(p: Path) -> bytes | None:
            try:
                if not p.is_file():
                    return None
                return p.read_bytes()
            except Exception:
                return None

        results_bytes = load_bytes(results_path)
        audit_bytes = load_bytes(audit_path)

        def verdict(name: str, local: bytes | None) -> str:
            if local is None:
                return f"- {name}: file not found"
            return (
                f"- {name}: MATCHES local file"
                if local == data
                else f"- {name}: DOES NOT MATCH local file"
            )

        lines = [
            f"CID: {cid}",
            "",
            verdict("results.json", results_bytes),
            verdict("audit_ledger.json", audit_bytes),
        ]
        QtWidgets.QMessageBox.information(
            self,
            "IPFS Verify",
            "\n".join(lines),
        )

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

    # --- Hardware / device checks -------------------------------------------------

    def _check_devices(self) -> None:
        """Check connection/initialization status of fingerprint/iris/camera.

        Runs a lightweight initialize-only check and reports status for each
        device. Uses try/except so that a missing driver never crashes the
        admin panel; instead the status is shown as "Missing (simulated)".
        """

        try:
            from hardware.device_manager import DeviceManager

            dm = DeviceManager()
            try:
                init_status = dm.initialize_all()
            except Exception:
                init_status = {}

            fp_available = getattr(dm.fingerprint, "available", True)
            iris_available = getattr(dm.retina, "available", True)
            cam_available = getattr(dm.camera, "available", True)

            # For the camera, also consider OpenCV access via index 0.
            opencv_camera_ok = False
            try:
                import cv2

                cap = cv2.VideoCapture(0)
                opencv_camera_ok = cap is not None and cap.isOpened()
                if cap is not None:
                    cap.release()
            except Exception:
                opencv_camera_ok = False

            def label(available: bool, ok: bool, *, also_ok: bool = False) -> str:
                effective_ok = ok or also_ok
                if not available and not effective_ok:
                    return "Missing (simulated)"
                return "OK" if effective_ok else "Error"

            msg = "Device Status:\n\n" + "\n".join(
                [
                    f"Fingerprint: {label(fp_available, init_status.get('fingerprint', False))}",
                    f"Iris: {label(iris_available, init_status.get('retina', False))}",
                    f"Camera: {label(cam_available, init_status.get('camera', False), also_ok=opencv_camera_ok)}",
                ]
            )
            QtWidgets.QMessageBox.information(self, "Device Status", msg)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Device Status",
                f"Could not check devices.\n\n{e}",
            )

    def _test_devices(self) -> None:
        """Run a simple capture test for each device.

        This is similar to the biometric capture screen's logic: if a
        device is present and capture succeeds it is marked "Real",
        otherwise it is reported as "Simulated" so the admin knows that
        path currently uses fallback behaviour.
        """

        real = {"fingerprint": False, "iris": False, "face": False}
        simulated = {"fingerprint": False, "iris": False, "face": False}

        try:
            from hardware.device_manager import DeviceManager

            dm = DeviceManager()
            try:
                init_status = dm.initialize_all()
            except Exception:
                init_status = {}
            try:
                capture_status = (
                    dm.capture_all() if init_status and all(init_status.values()) else {}
                )
            except Exception:
                capture_status = {}

            fp_available = getattr(dm.fingerprint, "available", False)
            iris_available = getattr(dm.retina, "available", False)
            cam_available = getattr(dm.camera, "available", False)

            if fp_available and capture_status.get("fingerprint"):
                real["fingerprint"] = True
            else:
                simulated["fingerprint"] = True

            if iris_available and capture_status.get("retina"):
                real["iris"] = True
            else:
                simulated["iris"] = True

            if cam_available and capture_status.get("camera"):
                real["face"] = True
            else:
                simulated["face"] = True
        except Exception:
            simulated = {k: True for k in simulated}

        def mode(is_real: bool) -> str:
            return "Real" if is_real else "Simulated"

        msg = (
            "Device Test Results:\n\n"
            f"Fingerprint: {mode(real['fingerprint'])}\n"
            f"Iris: {mode(real['iris'])}\n"
            f"Camera/Face: {mode(real['face'])}"
        )
        QtWidgets.QMessageBox.information(self, "Device Test", msg)


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
