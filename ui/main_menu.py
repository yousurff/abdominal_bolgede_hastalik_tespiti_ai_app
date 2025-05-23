# ui/main_menu.py
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal

class ImageDropLabel(QLabel):
    imageDropped = pyqtSignal(str)

    def __init__(self):
        super().__init__("Drag & Drop an image here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()

    def dropEvent(self, ev):
        path = ev.mimeData().urls()[0].toLocalFile()
        self.imageDropped.emit(path)

class MainMenuWindow(QWidget):
    def __init__(self, on_select_image, on_saved_images):
        super().__init__()
        self.on_select_image = on_select_image
        self.on_saved_images = on_saved_images
        self.setup_ui()

    def setup_ui(self):
        self.lbl_doctor   = QLabel("Dr. Yusuf", alignment=Qt.AlignmentFlag.AlignCenter)
        self.drop_area    = ImageDropLabel()
        self.drop_area.imageDropped.connect(self.handle_image)

        btn_select = QPushButton("Select Image")
        btn_select.clicked.connect(self.open_file_dialog)
        btn_saved  = QPushButton("Saved Images")
        btn_saved.clicked.connect(self.on_saved_images)

        layout = QVBoxLayout(self)
        layout.addWidget(self.lbl_doctor)
        layout.addWidget(self.drop_area, stretch=1)
        layout.addWidget(btn_select)
        layout.addWidget(btn_saved)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose Image", filter="Images (*.png *.jpg)")
        if path:
            self.handle_image(path)

    def handle_image(self, path):
        self.on_select_image(path)