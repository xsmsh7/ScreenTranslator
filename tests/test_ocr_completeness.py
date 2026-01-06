import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from services.ocr_service import OCRService
from PIL import Image

class TestOCRCompleteness(unittest.TestCase):
    def setUp(self):
        self.service = OCRService()
        self.mock_image = Image.new('RGB', (100, 100))

    @patch('services.ocr_service.pytesseract.image_to_data')
    def test_multi_block_detection(self, mock_image_to_data):
        """
        Verify that we are using a PSM mode that supports multiple blocks.
        If we use PSM 6, Tesseract assumes a SINGLE block.
        We want to ensure the configuration allows for multiple blocks (PSM 3).
        """
        # Mock return data doesn't strictly matter for the config check, 
        # but we need a valid DataFrame to pass the parsing logic.
        mock_data = pd.DataFrame({
            'text': ['Hello', 'World'],
            'block_num': [1, 2],  # Distinct blocks
            'line_num': [1, 1],
            'left': [0, 0], 'top': [0, 0], 'width': [10, 10], 'height': [10, 10],
            'conf': [90, 90]
        })
        mock_image_to_data.return_value = mock_data

        # Execute
        self.service.perform_ocr(self.mock_image)

        # Verify Code
        # We need to inspect the 'config' argument passed to Tesseract
        args, kwargs = mock_image_to_data.call_args
        config_used = kwargs.get('config', '')
        
        # FAIL condition: If we are still using psm 6
        if '--psm 6' in config_used:
            self.fail(f"OCR Service is configured with {config_used}. PSM 6 (Single Block) causes data loss on large selections.")

        # PASS condition: We expect psm 3 (Auto) or similar
        print(f"Verified Config: {config_used}")
        self.assertTrue('--psm 3' in config_used or '--psm 11' in config_used or '--psm 1' in config_used, 
                        "Should use an auto-segmentation mode (PSM 3)")

if __name__ == '__main__':
    unittest.main()
