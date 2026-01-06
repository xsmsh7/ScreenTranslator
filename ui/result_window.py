from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QPushButton, QScrollArea
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles import load_styles

class ResultWindow(QWidget):
    capture_requested = pyqtSignal()
    provider_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translation Result")
        self.resize(600, 500)

        
        layout = QVBoxLayout()
        
        self.image_label = QLabel("Waiting for capture...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        
        self.original_text_display = QTextEdit()
        self.original_text_display.setPlaceholderText("Captured Text...")
        self.original_text_display.setReadOnly(True)
        self.original_text_display.setMaximumHeight(80)
        
        self.translated_text_display = QTextEdit()
        self.translated_text_display.setPlaceholderText("Translated Text...")
        self.translated_text_display.setReadOnly(True)
        self.translated_text_display.setMaximumHeight(120)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["google", "openai"])
        
        self.btn_new_capture = QPushButton("New Selection")
        self.btn_new_capture.setObjectName("CaptureButton")
        
        layout.addWidget(QLabel("Visual Overlay:"))
        layout.addWidget(self.scroll_area, 1)
        layout.addWidget(QLabel("Original Text:"))
        layout.addWidget(self.original_text_display)
        layout.addWidget(QLabel("Translated Text:"))
        layout.addWidget(self.translated_text_display)
        layout.addWidget(QLabel("Provider:"))
        layout.addWidget(self.provider_combo)
        layout.addWidget(self.btn_new_capture)
        
        self.setLayout(layout)
        self.setStyleSheet(load_styles())
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        # Connect internal signals to external emitters
        self.btn_new_capture.clicked.connect(self.capture_requested.emit)
        self.provider_combo.currentTextChanged.connect(self.provider_changed.emit)

    def update_display(self, original_text, translated_text, pil_image):
        self.original_text_display.setText(original_text)
        self.translated_text_display.setText(translated_text)
        if pil_image:
            q_img = self.pil_to_qimage(pil_image)
            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setPixmap(pixmap)
        
        if not self.isVisible():
            self.show()
        self.activateWindow()

    def pil_to_qimage(self, pil_img):
        if pil_img.mode == "RGB":
            data = pil_img.tobytes("raw", "RGB")
            stride = pil_img.width * 3
            img = QImage(data, pil_img.width, pil_img.height, stride, QImage.Format.Format_RGB888)
            return img.copy()
        elif pil_img.mode == "RGBA":
            data = pil_img.tobytes("raw", "RGBA")
            stride = pil_img.width * 4
            img = QImage(data, pil_img.width, pil_img.height, stride, QImage.Format.Format_RGBA8888)
            return img.copy()
        return QImage()

    def closeEvent(self, event):
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
        event.accept()
