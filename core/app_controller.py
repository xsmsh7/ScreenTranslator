import threading
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject

from ui.result_window import ResultWindow
from ui.capture_overlay import CaptureOverlay
from services.ocr_service import OCRService
from services.translator_service import TranslatorFactory
from utils import helpers as utils
from PIL import ImageDraw, ImageFont

class AppController(QObject):
    update_ui_signal = pyqtSignal(str, object)

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.ocr_service = OCRService()
        self.result_window = ResultWindow()
        
        # Connect UI signals
        self.result_window.capture_requested.connect(self.start_capture)
        self.result_window.provider_changed.connect(self.trigger_retranslate)
        self.update_ui_signal.connect(self.result_window.update_display)
        
        self._setup_tray()
        self.last_image = None

    def _setup_tray(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme("edit-find")) 
        
        tray_menu = QMenu()
        capture_action = QAction("Capture Screen", self.tray_icon)
        capture_action.triggered.connect(self.start_capture)
        
        quit_action = QAction("Quit", self.tray_icon)
        quit_action.triggered.connect(self.app.quit)
        
        tray_menu.addAction(capture_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def start_capture(self):
        self.result_window.hide()
        self.overlay_window = CaptureOverlay()
        self.overlay_window.capture_complete.connect(self.handle_capture)
        self.overlay_window.capture_cancelled.connect(self.result_window.show)
        self.overlay_window.show()

    def handle_capture(self, image):
        self.last_image = image
        self.result_window.show()
        self.result_window.image_label.setText("Processing...")
        self.trigger_retranslate()

    def trigger_retranslate(self):
        if self.last_image:
            threading.Thread(target=self.process_image_threaded, args=(self.last_image,), daemon=True).start()

    def process_image_threaded(self, image):
        try:
            # Perform OCR
            data = self.ocr_service.perform_ocr(image)
            if data is None or data.empty:
                self.update_ui_signal.emit("No text found", image)
                return

            # Get Translator
            provider = self.result_window.provider_combo.currentText()
            translator = TranslatorFactory.get_translator(provider)
            
            # Prepare overlay image
            translated_img = image.copy()
            draw = ImageDraw.Draw(translated_img)
            font_path = utils.get_font_path()
            
            # Grouping and Translation logic
            lines = data.groupby(['block_num', 'line_num'])
            full_original_text = []
            
            for _, group in lines:
                line_text = " ".join(group.text.astype(str)).strip()
                if not line_text: continue
                
                full_original_text.append(line_text)
                translated_text = translator.translate(line_text)
                
                # Draw logic
                x_min, y_min = group.left.min(), group.top.min()
                x_max, y_max = (group.left + group.width).max(), (group.top + group.height).max()
                
                # Draw background
                draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white")
                
                # Draw text
                h = y_max - y_min
                font_size = max(12, int(h * 0.9))
                try:
                    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
                
                draw.text((x_min, y_min), translated_text, fill="black", font=font)

            self.update_ui_signal.emit("\n".join(full_original_text), translated_img)
        except Exception as e:
            print(f"Controller Error: {e}")
            self.update_ui_signal.emit(f"Error: {e}", None)

    def run(self):
        self.start_capture()
        return self.app.exec()
