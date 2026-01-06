import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

# This import will fail initially, demonstrating TDD "Red" phase
# We plan to extract this logic to services/drawing_service.py
try:
    from services.drawing_service import draw_translation_overlay
except ImportError:
    draw_translation_overlay = None

class TestOverlayRendering(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (100, 100), color='white')
        self.metadata = [
            {'box': (10, 10, 50, 20), 'original': 'Hello'},
            {'box': (10, 30, 50, 40), 'original': 'World'}
        ]
        self.translations = ['Ni Hao', 'Shijie']

    @patch('PIL.ImageDraw.Draw')
    @patch('utils.helpers.get_font_path', return_value=None) 
    def test_two_pass_rendering_order(self, mock_font, mock_draw_cls):
        """
        Verify that ALL background rectangles are drawn BEFORE any text.
        This ensures high-contrast backgrounds don't overwrite previously drawn text.
        """
        if draw_translation_overlay is None:
            self.fail("Implementation unimplemented: draw_translation_overlay not found")

        # Setup Mock
        mock_draw_instance = MagicMock()
        mock_draw_cls.return_value = mock_draw_instance
        # Mock textbbox to return a valid box (left, top, right, bottom)
        # So text_w = 40 - 0 = 40. box_w in test is 50-10=40.
        mock_draw_instance.textbbox.return_value = (0, 0, 40, 10)
        
        # Execute
        draw_translation_overlay(self.image, self.metadata, self.translations)
        
        # Analyze Calls
        # We expect: rect, rect, ..., text, text
        calls = mock_draw_instance.mock_calls
        
        rectangle_indices = [i for i, call in enumerate(calls) if 'rectangle' in call[0]]
        text_indices = [i for i, call in enumerate(calls) if 'text' in call[0] and 'bbox' not in call[0]] # bbox check excluded
        
        self.assertTrue(len(rectangle_indices) > 0, "Should draw background rectangles")
        self.assertTrue(len(text_indices) > 0, "Should draw text")
        
        last_rectangle_index = max(rectangle_indices)
        first_text_index = min(text_indices)
        
        print(f"Last Rectangle at: {last_rectangle_index}, First Text at: {first_text_index}")
        
        self.assertLess(last_rectangle_index, first_text_index, 
                        "Violation of Two-Pass Rendering: A rectangle was drawn after text started!")

if __name__ == '__main__':
    unittest.main()
