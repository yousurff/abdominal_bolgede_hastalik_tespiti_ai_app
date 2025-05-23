# ui/saved_images_window.py

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QAbstractItemView,
    QDialog, QLabel, QScrollArea
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

from utils.image_utils import SAVE_DIR


class SavedImagesWindow(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        # entries: list of (name: str, note: str, timestamp: datetime, path: str)
        self.entries = []
        self.setup_ui()
        self._load_existing_entries()
        self.refresh_table()

    def setup_ui(self):
        # Search bar
        self.search = QLineEdit(placeholderText="Search by name…")
        self.search.textChanged.connect(self.refresh_table)

        # Table with 5 columns: Thumb | Name | Note | Date | Time
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["", "Name", "Note", "Date", "Time"]
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setIconSize(QSize(80, 80))

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 80)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Double‐click to preview
        self.table.cellDoubleClicked.connect(self.on_preview)

        # Back button
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.on_back)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.table, stretch=1)
        layout.addWidget(btn_back)

    def _load_existing_entries(self):
        if not os.path.isdir(SAVE_DIR):
            return

        # load all notes
        from utils.image_utils import _load_metadata
        meta = _load_metadata()

        for fname in sorted(os.listdir(SAVE_DIR)):
            if not fname.lower().endswith(".png"):
                continue
            base = fname[:-4]
            if "_" not in base:
                continue
            name, ts_str = base.split("_", 1)
            try:
                ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            except ValueError:
                continue
            full_path = os.path.join(SAVE_DIR, fname)
            note = meta.get(fname, "")  # lookup the saved note
            self.entries.append((name, note, ts, full_path))

    def add_entry(self, name: str, note: str, timestamp: datetime, path: str):
        self.entries.append((name, note, timestamp, path))
        self.refresh_table()

    def refresh_table(self):
        text = self.search.text().lower()
        self.table.setRowCount(0)

        for name, note, ts, path in self.entries:
            if text and text not in name.lower():
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            # --- Thumbnail ---
            pix = QPixmap(path)
            thumb = pix.scaled(
                80, 80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            item_icon = QTableWidgetItem()
            item_icon.setIcon(QIcon(thumb))
            item_icon.setData(Qt.ItemDataRole.UserRole, path)
            self.table.setItem(row, 0, item_icon)

            # --- Name ---
            self.table.setItem(row, 1, QTableWidgetItem(name))

            # --- Note (first line only) ---
            first_line = note.splitlines()[0] if note else ""
            self.table.setItem(row, 2, QTableWidgetItem(first_line))

            # --- Date & Time ---
            self.table.setItem(row, 3,
                               QTableWidgetItem(ts.strftime("%Y-%m-%d")))
            self.table.setItem(row, 4,
                               QTableWidgetItem(ts.strftime("%H:%M:%S")))

    def on_preview(self, row, _col):
        # retrieve stored data
        item = self.table.item(row, 0)
        path = item.data(Qt.ItemDataRole.UserRole)
        name = self.table.item(row, 1).text()
        # look up full note
        note = ""
        for n, full_note, ts, p in self.entries:
            if p == path:
                note = full_note
                break

        pix = QPixmap(path)
        if pix.isNull():
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"{name} — Preview")
        dlg.resize(1000, 600)

        # Left: scrollable image
        scroll = QScrollArea(dlg)
        lbl_img = QLabel()
        lbl_img.setPixmap(pix)
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setWidget(lbl_img)
        scroll.setWidgetResizable(True)

        # Right: name and full note
        info_layout = QVBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-weight: bold; font-size: 16px;")
        info_layout.addWidget(lbl_name)

        if note:
            lbl_note = QLabel(note)
            lbl_note.setWordWrap(True)
            # Clip to 1 line in the table, but here show full note
            info_layout.addWidget(lbl_note)

        info_layout.addStretch(1)

        # Combine horizontally
        from PyQt6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(dlg)
        layout.addWidget(scroll, stretch=3)
        layout.addLayout(info_layout, stretch=1)

        dlg.exec()