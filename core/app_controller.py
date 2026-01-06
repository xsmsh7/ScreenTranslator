import threading
import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QObject

from ui.result_window import ResultWindow
from ui.capture_overlay import CaptureOverlay
from services.ocr_service import OCRService
from services.translator_service import TranslatorFactory
from services.drawing_service import draw_translation_overlay
from utils import helpers as utils
from PIL import ImageDraw, ImageFont

class AppController(QObject):
    update_ui_signal = pyqtSignal(str, str, object)  # (original_text, translated_text, image)

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
                self.update_ui_signal.emit("No text found", "", image)
                return

            # Get Translator
            provider = self.result_window.provider_combo.currentText()
            translator = TranslatorFactory.get_translator(provider)
            
            # Prepare overlay image
            translated_img = image.copy()

            
            # 1. Collect lines and Prepare translation groups
            groups = data.groupby(['block_num', 'line_num'])
            lines_metadata = []
            original_texts = []
            
            for _, group in groups:
                line_text = " ".join(group.text.astype(str)).strip()
                if not line_text: continue
                
                original_texts.append(line_text)
                
                # Calculate bounding box for this line
                x_min, y_min = group.left.min(), group.top.min()
                x_max, y_max = (group.left + group.width).max(), (group.top + group.height).max()
                lines_metadata.append({
                    'original': line_text,
                    'box': (x_min, y_min, x_max, y_max)
                })

            if not original_texts:
                self.update_ui_signal.emit("No translatable text found", "", image)
                return

            # 2. BATCH TRANSLATION: Join lines for better context and speed
            full_original_block = "\n".join(original_texts)
            translated_block = translator.translate(full_original_block) or ""
            translated_lines = translated_block.split("\n")
            
            # Ensure we have a match for each line; pad if necessary
            if len(translated_lines) < len(original_texts):
                translated_lines.extend([""] * (len(original_texts) - len(translated_lines)))

            # 3. Draw Overlay
            draw_translation_overlay(translated_img, lines_metadata, translated_lines)
            
            # Prepare translated text for UI display (copyable)
            translated_block = "\n".join(translated_lines)

            self.update_ui_signal.emit("\n".join(original_texts), translated_block, translated_img)
        except Exception as e:
            print(f"Controller Error: {e}")
            self.update_ui_signal.emit(f"Error: {e}", "", None)

    def run(self):
        self.start_capture()
        return self.app.exec()
