import pytesseract
from utils import helpers as utils

# Set tesseract cmd
pytesseract.pytesseract.tesseract_cmd = utils.get_tesseract_cmd()

class OCRService:
    def perform_ocr(self, image):
        """
        Extracts words and their locations from an image.
        """
        try:
            # Get detailed OCR data (including bounding boxes)
            data = pytesseract.image_to_data(image, lang='eng', config='--psm 6', output_type=pytesseract.Output.DATAFRAME)
            
            # Filter out empty text detections and cast to string
            data = data[data.text.notna()]
            data['text'] = data['text'].astype(str)
            data = data[data['text'].str.strip() != ""]
            
            return data
        except Exception as e:
            print(f"OCR Service Error: {e}")
            return None
