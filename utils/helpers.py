import os
import sys

def get_tesseract_cmd():
    """Returns the path to the tesseract executable."""
    # Common Windows paths
    paths = [
        r'C:\Users\RD\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Users\RD\AppData\Local\Tesseract-OCR\tesseract.exe'
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return 'tesseract' # Hope it's in PATH

def get_openai_api_key():
    """Retrieves OpenAI API key from environment or project file."""
    # Look for .env first
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    return line.split('=')[1].strip()
    return os.getenv("OPENAI_API_KEY")

def get_font_path():
    """Returns a path to a valid Chinese-supporting font on Windows."""
    paths = [
        r'C:\Windows\Fonts\msyh.ttc', # Microsoft YaHei
        r'C:\Windows\Fonts\simhei.ttf', # SimHei
        r'C:\Windows\Fonts\SimSun.ttc', # SimSun
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None
