import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QDialog,
    QInputDialog,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QFormLayout
)
from datetime import datetime
from utils.image_utils import save_image
from ui.login_window import LoginWindow
from ui.main_menu import MainMenuWindow
from ui.detection_window import DetectionWindow
from ui.saved_images_window import SavedImagesWindow

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # instantiate pages
        self.login_page = LoginWindow(on_success=self.show_main)
        self.main_menu = MainMenuWindow(
            on_select_image=self.show_detection,
            on_saved_images=self.show_saved
        )
        self.detection_page = DetectionWindow(
            on_save=self.show_save_dialog,
            on_back=lambda: self.stack.setCurrentWidget(self.main_menu)
        )
        self.saved_page = SavedImagesWindow(on_back=lambda: self.stack.setCurrentWidget(self.main_menu))

        # add to stack
        for w in (self.login_page, self.main_menu, self.detection_page, self.saved_page):
            self.stack.addWidget(w)

        # start on login
        self.stack.setCurrentWidget(self.login_page)
        self.setWindowTitle("Omega Vizyon")

    def show_main(self):
        self.stack.setCurrentWidget(self.main_menu)

    def show_detection(self, image_path):
        self.detection_page.load_image_and_detect(image_path)
        self.stack.setCurrentWidget(self.detection_page)

    def show_saved(self):
        self.saved_page.refresh_table()
        self.stack.setCurrentWidget(self.saved_page)

    def show_save_dialog(self, processed_image):
        # Create a modal dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Save Image and Note")

        form = QFormLayout(dlg)
        name_edit = QLineEdit()
        note_edit = QTextEdit()
        note_edit.setFixedHeight(80)  # limit its height

        form.addRow("Name:", name_edit)
        form.addRow("Note:", note_edit)

        # OK / Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel,
            parent=dlg
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        form.addRow(buttons)

        # Show the dialog
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name  = name_edit.text().strip()
            note  = note_edit.toPlainText().strip()
            timestamp = datetime.now()
            # <-- pass note into save_image now
            path = save_image(processed_image, name, timestamp, note)
            self.saved_page.add_entry(name, note, timestamp, path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())