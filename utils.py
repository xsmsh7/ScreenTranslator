import os
import sys

# Default path for Tesseract - users might need to change this
# Common paths for Windows
TESSERACT_CMD = r'C:\Users\RD\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def get_tesseract_cmd():
    """Returns the configured Tesseract command path."""
    # You could add logic here to check env vars or config files
    return TESSERACT_CMD

def get_openai_api_key():
    """Retrieves OpenAI API key from environment variable."""
    return os.getenv("OPENAI_API_KEY")

def load_styles():
    """Returns basic QSS styles for the app."""
    return """
        QMainWindow, QWidget#Main {
            background-color: white;
        }
        QPushButton#CaptureButton {
            background-color: #28a745;
            margin-top: 10px;
            font-weight: bold;
        }
        QPushButton#CaptureButton:hover {
            background-color: #218838;
        }
        QPushButton {
            background-color: #0078D7;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #0063B1;
        }
        QTextEdit {
            background-color: #F3F3F3;
            border: 1px solid #E5E5E5;
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
        }
        QLabel {
            font-size: 12px;
            font-weight: bold;
        }
    """
