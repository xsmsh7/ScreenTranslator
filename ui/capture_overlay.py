from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
import mss
from PIL import Image

class CaptureOverlay(QWidget):
    capture_complete = pyqtSignal(object)  # Signal emitting PIL Image
    capture_cancelled = pyqtSignal()       # Signal for cancellation

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.start_point = None
        self.end_point = None
        self.is_selecting = False

        self.opacity_color = QColor(0, 0, 0, 100) # Semi-transparent black
        self.selection_border_color = QColor(0, 120, 215)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(self.opacity_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        if self.start_point and self.end_point:
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.drawRect(selection_rect)
            
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
            self.close() 
            self.capture_screen_area()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            self.capture_cancelled.emit()

    def capture_screen_area(self):
        if not self.start_point or not self.end_point:
            return

        rect = QRect(self.start_point, self.end_point).normalized()
        if rect.width() < 5 or rect.height() < 5:
            return 
        
        with mss.mss() as sct:
            monitor = {
                "top": rect.top(),
                "left": rect.left(),
                "width": rect.width(),
                "height": rect.height(),
            }
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            self.capture_complete.emit(img)
