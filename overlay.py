import sys
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QGuiApplication
import mss
from PIL import Image

class CaptureOverlay(QWidget):
    capture_complete = pyqtSignal(object)  # Signal emitting PIL Image
    capture_cancelled = pyqtSignal()       # New signal for cancellation

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # Capture the whole screen initially to show a static "freeze" (optional, but good for performance)
        # For simplicity here, we just draw a transparent overlay
        
        self.start_point = None
        self.end_point = None
        self.is_selecting = False

        self.opacity_color = QColor(0, 0, 0, 100) # Semi-transparent black
        self.selection_border_color = QColor(0, 120, 215)
        self.selection_fill_color = QColor(255, 255, 255, 0) # Transparent inside

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the dark overlay over the whole screen
        painter.setBrush(QBrush(self.opacity_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        if self.start_point and self.end_point:
            # Calculate selection rect
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Clear the part of the overlay where the selection is
            # We do this by setting current clip to the selection and filling with transparent
            # Actually easier: Draw the hole.
            # Painter composition mode 'CompositionMode_Clear' cuts a hole
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.drawRect(selection_rect)
            
            # Reset composition mode to draw border
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(self.selection_border_color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_point = event.pos()
            self.is_selecting = False
            self.close() # Close overlay immediately
            
            # Perform capture
            self.capture_screen_area()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.capture_cancelled.emit()

    def capture_screen_area(self):
        if not self.start_point or not self.end_point:
            return

        # Normalize coordinates
        rect = QRect(self.start_point, self.end_point).normalized()
        
        if rect.width() < 5 or rect.height() < 5:
            return # Too small
        
        # MSS Capture
        with mss.mss() as sct:
            # We need to account for multiple monitors potentially, but simpler logic first
            # mapFromGlobal might be needed if not fullscreen on all screens.
            # Since we set WindowFullScreen, self.geometry() should cover the active screen logic mostly.
            # But let's use the rect relative to the screen.
            
            monitor = {
                "top": rect.top(),
                "left": rect.left(),
                "width": rect.width(),
                "height": rect.height(),
            }
            
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            
            self.capture_complete.emit(img)
