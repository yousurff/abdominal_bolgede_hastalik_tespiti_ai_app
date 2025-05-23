# ui/detection_window.py

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore     import Qt
from PyQt6.QtGui      import QPixmap, QImage
import cv2

from models.object_detector import detect_objects

def array_to_qimage(img_array):
    """
    Convert a BGR OpenCV image (NumPy array) to a QImage (RGB888).
    """
    height, width, channel = img_array.shape
    bytes_per_line = channel * width
    # Convert from BGR (OpenCV) to RGB
    rgb_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    return QImage(
        rgb_img.data,
        width,
        height,
        bytes_per_line,
        QImage.Format.Format_RGB888
    )

class DetectionWindow(QWidget):
    def __init__(self, on_save, on_back):
        super().__init__()
        self.on_save = on_save
        self.on_back = on_back
        self.setup_ui()

    def setup_ui(self):
        # CENTER the label
        self.img_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_save  = QPushButton("Save Image")
        self.btn_back  = QPushButton("Return to Main Menu")
        self.btn_save.clicked.connect(self.save)
        self.btn_back.clicked.connect(self.on_back)

        layout = QVBoxLayout(self)
        layout.addWidget(self.img_label, stretch=1)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_back)

    def load_image_and_detect(self, path):
        # Run your AI model
        processed_image, bboxes = detect_objects(path)

        # Convert NumPy → QImage → QPixmap
        qimg = array_to_qimage(processed_image)
        pix  = QPixmap.fromImage(qimg)
        # Scale to fit label while keeping aspect ratio
        self.img_label.setPixmap(
            pix.scaled(self.img_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        )

        # Store for saving
        self._last_image = processed_image

    def save(self):
        # Call back into AppWindow.show_save_dialog
        self.on_save(self._last_image)