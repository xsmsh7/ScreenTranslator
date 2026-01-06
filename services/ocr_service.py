import pytesseract
from utils import helpers as utils

# Set tesseract cmd
pytesseract.pytesseract.tesseract_cmd = utils.get_tesseract_cmd()


# Try to import WindowsOCR, but don't crash if dependencies aren't ready
try:
    from services.windows_ocr import WindowsOCR
    HAS_WINDOWS_OCR = True
except ImportError:
    HAS_WINDOWS_OCR = False

class OCRService:
    def __init__(self):
        self.windows_provider = None
        if HAS_WINDOWS_OCR:
            try:
                self.windows_provider = WindowsOCR()
                print("OCR Strategy: Used Windows Native OCR")
            except Exception as e:
                print(f"Failed to initialize Windows OCR: {e}")

    def perform_ocr(self, image):
        """
        Extracts words and their locations from an image.
        Strategy: Try Windows Native OCR first -> Fallback to Tesseract.
        """
        # Strategy 1: Windows Native OCR
        if self.windows_provider:
            data = self.windows_provider.perform_ocr(image)
            if data is not None and not data.empty:
                return data
            # If Windows OCR returns None/Empty (unexpected failure), fall through to Tesseract? 
            # Or return empty?
            # Let's fallback only on hard error, but 'perform_ocr' returns None on error.
            if data is None: 
                print("Windows OCR failed (None), falling back to Tesseract.")
            else:
                return data # Return empty dataframe if nothing found

        # Strategy 2: Tesseract (Fallback)
        try:
            # Get detailed OCR data (including bounding boxes)
            # Use PSM 3 (Auto segmentation) to handle multiple text blocks/columns correctly
            data = pytesseract.image_to_data(image, lang='eng', config='--psm 3', output_type=pytesseract.Output.DATAFRAME)
            
            # Filter out empty text detections and cast to string
            if data is not None and not data.empty:
                data = data[data.text.notna()]
                data['text'] = data['text'].astype(str)
                data = data[data['text'].str.strip() != ""]
            
            return data
        except Exception as e:
            print(f"OCR Service (Tesseract) Error: {e}")
            return None
