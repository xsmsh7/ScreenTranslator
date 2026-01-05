import sys
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QPushButton, QLabel, QSystemTrayIcon, QMenu, 
                             QComboBox, QScrollArea)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

import overlay
import translator_service
import utils
from PIL import Image
import io

class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translation Result")
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # New: Image display area
        self.image_label = QLabel("Waiting for capture...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        
        self.original_text_display = QTextEdit()
        self.original_text_display.setPlaceholderText("Captured Text...")
        self.original_text_display.setReadOnly(True)
        self.original_text_display.setMaximumHeight(80)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["google", "openai"])
        
        self.btn_new_capture = QPushButton("New Selection")
        self.btn_new_capture.setObjectName("CaptureButton")
        
        layout.addWidget(QLabel("Visual Overlay:"))
        layout.addWidget(self.scroll_area, 1) # Give it stretch
        layout.addWidget(QLabel("Original Text:"))
        layout.addWidget(self.original_text_display)
        layout.addWidget(QLabel("Provider:"))
        layout.addWidget(self.provider_combo)
        layout.addWidget(self.btn_new_capture)
        
        self.setLayout(layout)
        self.setStyleSheet(utils.load_styles())
        
        # Keep window on top
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def update_content(self, original, pil_image):
        self.original_text_display.setText(original)
        
        # Convert PIL Image to QPixmap
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
            return img.copy() # Copy to ensure data ownership
        elif pil_img.mode == "RGBA":
            data = pil_img.tobytes("raw", "RGBA")
            stride = pil_img.width * 4
            img = QImage(data, pil_img.width, pil_img.height, stride, QImage.Format.Format_RGBA8888)
            return img.copy()
        return QImage()

class ScreenTranslatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.translator = translator_service.TranslatorService()
        self.result_window = ResultWindow()
        self.result_window.btn_new_capture.clicked.connect(self.start_capture)
        self.result_window.provider_combo.currentTextChanged.connect(self.trigger_retranslate)
        
        # System Tray
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme("edit-find")) 
        
        tray_menu = QMenu()
        capture_action = QAction("Capture Screen", self.app)
        capture_action.triggered.connect(self.start_capture)
        
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.app.quit)
        
        tray_menu.addAction(capture_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.last_image = None

    def start_capture(self):
        self.result_window.hide()  # Hide the result window
        self.overlay_window = overlay.CaptureOverlay()
        self.overlay_window.capture_complete.connect(self.handle_capture)
        self.overlay_window.capture_cancelled.connect(self.handle_cancel) # Connect cancel signal
        self.overlay_window.show()

    def handle_cancel(self):
        self.result_window.show()

    def handle_capture(self, image):
        self.last_image = image
        self.result_window.show() # Show window immediately
        self.result_window.image_label.setText("Processing OCR & Translation...")
        self.trigger_retranslate()

    def trigger_retranslate(self):
        if self.last_image:
            threading.Thread(target=self.process_image_threaded, args=(self.last_image,)).start()

    def process_image_threaded(self, image):
        try:
            # Add a small limit to image size for stability
            if image.width > 2000 or image.height > 2000:
                image.thumbnail((2000, 2000))
                
            provider = self.result_window.provider_combo.currentText()
            translated_img, original_text = self.translator.overlay_translation(image, provider=provider)
            # Emit signal to update UI
            monitor.update_ui.emit(original_text, translated_img)
        except Exception as e:
            print(f"Thread Error: {e}")
            monitor.update_ui.emit(f"Error: {e}", None)

class WorkerSignal(QWidget):
    update_ui = pyqtSignal(str, object)

if __name__ == "__main__":
    main_app = ScreenTranslatorApp()
    monitor = WorkerSignal()
    monitor.update_ui.connect(main_app.result_window.update_content)
    
    # Auto start capture
    main_app.start_capture()
    sys.exit(main_app.app.exec())
