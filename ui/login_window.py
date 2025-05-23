# ui/login_window.py

import os
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QLabel,
    QDialog, QFormLayout, QDialogButtonBox, QHBoxLayout, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image

class NewUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New User")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Logo at top with Qt + PIL fallback
        logo_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        logo_path = os.path.join(proj_root, "resources", "omega_logo.png")
        pix = QPixmap(logo_path)
        if pix.isNull():
            # PIL fallback
            try:
                img = Image.open(logo_path)
                img.thumbnail((200, 200), Image.LANCZOS)
                img = img.convert("RGBA")
                data = img.tobytes("raw", "RGBA")
                qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
                pix = QPixmap.fromImage(qimg)
            except Exception as e:
                print("⚠️ Logo fallback failed:", e)
        if not pix.isNull():
            pix = pix.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)

        layout.addWidget(logo_label)

        # Form fields
        form = QFormLayout()
        self.name_edit    = QLineEdit()
        self.surname_edit = QLineEdit()
        self.dob_edit     = QDateEdit(calendarPopup=True)
        self.dob_edit.setDate(QDate.currentDate())
        self.user_edit    = QLineEdit()
        self.pass_edit    = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        self.conf_edit    = QLineEdit(echoMode=QLineEdit.EchoMode.Password)

        form.addRow("Name:", self.name_edit)
        form.addRow("Surname:", self.surname_edit)
        form.addRow("Date of Birth:", self.dob_edit)
        form.addRow("Username:", self.user_edit)
        form.addRow("Password:", self.pass_edit)
        form.addRow("Confirm Password:", self.conf_edit)
        layout.addLayout(form)

        # Buttons row
        btn_layout = QHBoxLayout()
        back_btn   = QPushButton("Back")
        create_btn = QPushButton("Create User")
        back_btn.clicked.connect(self.reject)
        create_btn.clicked.connect(self.create_user)
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(create_btn)
        layout.addLayout(btn_layout)

    def create_user(self):
        if self.pass_edit.text() != self.conf_edit.text():
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        usb_dlg = USBPasswordDialog(self)
        usb_dlg.exec()
        self.accept()


class USBPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert USB Password")
        layout = QVBoxLayout(self)
        lbl = QLabel("Insert USB password!")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Logo at top with Qt + PIL fallback
        logo_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        proj_root  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        logo_path  = os.path.join(proj_root, "resources", "omega_logo.png")
        pix = QPixmap(logo_path)
        if pix.isNull():
            try:
                img = Image.open(logo_path)
                img.thumbnail((200, 200), Image.LANCZOS)
                img = img.convert("RGBA")
                data = img.tobytes("raw", "RGBA")
                qimg = QImage(data, img.width, img.height, QImage.Format.Format_RGBA8888)
                pix = QPixmap.fromImage(qimg)
            except Exception as e:
                print("⚠️ Logo fallback failed:", e)
        if not pix.isNull():
            pix = pix.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        layout.addWidget(logo_label)

        layout.addStretch(1)

        # Username / Password
        self.user_input = QLineEdit(placeholderText="Username")
        self.pass_input = QLineEdit(
            placeholderText="Password",
            echoMode=QLineEdit.EchoMode.Password
        )
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)

        # Buttons row: Login | New User
        btn_row = QHBoxLayout()
        login_btn   = QPushButton("Login")
        newuser_btn = QPushButton("New User")
        login_btn.clicked.connect(self.check_credentials)
        newuser_btn.clicked.connect(self.open_new_user)
        btn_row.addWidget(login_btn)
        btn_row.addWidget(newuser_btn)
        layout.addLayout(btn_row)

    def check_credentials(self):
        if (self.user_input.text(), self.pass_input.text()) == ("yusuf", "123"):
            self.on_success()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def open_new_user(self):
        dlg = NewUserDialog(self)
        dlg.exec()