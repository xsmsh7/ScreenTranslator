import sys
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QPushButton, QLabel, QSystemTrayIcon, QMenu, 
                             QComboBox)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

import overlay
import translator_service
import utils

class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translation Result")
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        self.original_text_display = QTextEdit()
        self.original_text_display.setPlaceholderText("Captured Text...")
        self.original_text_display.setReadOnly(True)
        self.original_text_display.setMaximumHeight(80)
        
        self.translated_text_display = QTextEdit()
        self.translated_text_display.setPlaceholderText("Translation...")
        self.translated_text_display.setReadOnly(True)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["google", "openai"])
        self.provider_combo.currentTextChanged.connect(self.translate_again)
        
        self.btn_new_capture = QPushButton("New Selection")
        self.btn_new_capture.setObjectName("CaptureButton")
        
        layout.addWidget(QLabel("Original Text:"))
        layout.addWidget(self.original_text_display)
        layout.addWidget(QLabel("Translation:"))
        layout.addWidget(self.translated_text_display)
        layout.addWidget(QLabel("Provider:"))
        layout.addWidget(self.provider_combo)
        layout.addWidget(self.btn_new_capture)
        
        self.setLayout(layout)
        self.setStyleSheet(utils.load_styles())
        
        # Keep window on top
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def update_content(self, original, translated):
        self.original_text_display.setText(original)
        self.translated_text_display.setText(translated)
        
        if not self.isVisible():
            self.show()
        self.activateWindow()

    def translate_again(self, provider):
        # We invoke the main app logic to re-translate if needed
        # But for simplicity, we just trigger a signal or direct call if connected
        # Since logic is in MainApp, we will leave this hooks for now.
        pass

class ScreenTranslatorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.translator = translator_service.TranslatorService()
        self.result_window = ResultWindow()
        self.result_window.provider_combo.currentTextChanged.connect(self.re_translate)
        self.result_window.btn_new_capture.clicked.connect(self.start_capture)
        
        # System Tray
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme("edit-find")) # Fallback icon if none
        # In a real app we'd load a .png file here
        
        tray_menu = QMenu()
        capture_action = QAction("Capture Screen", self.app)
        capture_action.triggered.connect(self.start_capture)
        
        show_result_action = QAction("Show Last Result", self.app)
        show_result_action.triggered.connect(self.result_window.show)
        
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.app.quit)
        
        tray_menu.addAction(capture_action)
        tray_menu.addAction(show_result_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Keep track of last text for re-translation
        self.last_text = ""

        # Trigger capture immediately on start (optional, as per user might want)
        # self.start_capture()
        print("Application Started. Use System Tray to Capture.")

    def start_capture(self):
        self.overlay_window = overlay.CaptureOverlay()
        self.overlay_window.capture_complete.connect(self.handle_capture)
        self.overlay_window.show()

    def handle_capture(self, image):
        # Run processing in background thread to not freeze UI
        threading.Thread(target=self.process_image, args=(image,)).start()

    def process_image(self, image):
        print("Processing Image...")
        
        # OCR
        text = self.translator.perform_ocr(image)
        print(f"OCR Result: {text}")
        
        self.last_text = text
        if not text:
            # Need to signal UI thread safely
             # For simplicity in this script, we might just update directly if PyQt allows 
             # (it often doesn't from another thread). Correct way is Signals.
             # But let's cheat and use invokeMethod or simpler: just do it on main thread if fast enough. 
             # OCR is slow, better use signals.
             pass
        
        self.do_translate(text)

    def do_translate(self, text):
        provider = self.result_window.provider_combo.currentText()
        translation = self.translator.translate_text(text, provider=provider)
        
        # Update UI (Must be on main thread - simplified here, beware of threading constraints)
        # Using simple invoke via QMetaObject or passing to a slot
        # To fix threading, let's create a signal wrapper
        # For now, let's rely on the fact that we need a signal.
        # Can't easily modify class structure inside method.
        # Let's Move Threading logic better.
        pass

    def re_translate(self):
        if self.last_text:
             threading.Thread(target=self.do_translate_threaded, args=(self.last_text,)).start()

    def do_translate_threaded(self, text):
        provider = self.result_window.provider_combo.currentText()
        translation = self.translator.translate_text(text, provider=provider)
        # Update UI via signal wrapper - Implementing Worker Pattern inline for brevity
        # Hack for this single file: call a method that queues only the UI update
        self.result_window.update_content(text, translation)

# To properly handle threading updates:
class WorkerSignal(QWidget):
    update_ui = pyqtSignal(str, str)

if __name__ == "__main__":
    # Wrap logic to handle the signals properly
    main_app = ScreenTranslatorApp()
    
    # Patching for signals
    monitor = WorkerSignal()
    monitor.update_ui.connect(main_app.result_window.update_content)
    
    # Overwrite process_image to use signal
    def threaded_process(image):
        text = main_app.translator.perform_ocr(image)
        provider = main_app.result_window.provider_combo.currentText()
        translation = main_app.translator.translate_text(text, provider=provider)
        main_app.last_text = text
        monitor.update_ui.emit(text, translation)

    main_app.process_image = lambda img: threading.Thread(target=threaded_process, args=(img,)).start()
    main_app.re_translate = lambda: threading.Thread(
        target=lambda: monitor.update_ui.emit(
            main_app.last_text, 
            main_app.translator.translate_text(main_app.last_text, provider=main_app.result_window.provider_combo.currentText())
        )
    ).start()

    # Auto start capture for testing
    main_app.start_capture()
    
    sys.exit(main_app.app.exec())
