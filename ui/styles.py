def load_styles():
    """Returns basic QSS styles for the app."""
    return """
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
        }
        QPushButton#CaptureButton {
            background-color: #0078d7;
            border: none;
            padding: 10px;
            color: white;
            font-weight: bold;
            border-radius: 4px;
        }
        QPushButton#CaptureButton:hover {
            background-color: #005a9e;
        }
        QTextEdit {
            background-color: #252526;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            padding: 5px;
        }
        QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #3e3e42;
            padding: 5px;
            border-radius: 4px;
        }
    """
