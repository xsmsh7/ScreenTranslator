import pytesseract
from deep_translator import GoogleTranslator
from openai import OpenAI
import utils
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# Set tesseract cmd
pytesseract.pytesseract.tesseract_cmd = utils.get_tesseract_cmd()

class TranslatorService:
    def __init__(self):
        self.google_translator = GoogleTranslator(source='auto', target='zh-CN')
        self.openai_client = None
        
        api_key = utils.get_openai_api_key()
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)

    def perform_ocr_with_data(self, image):
        """
        Extracts words and their locations from an image.
        """
        try:
            # Get detailed OCR data (including bounding boxes)
            # Use --psm 6 to assume uniform block of text (prevents wild layout detection on small clips)
            data = pytesseract.image_to_data(image, lang='eng', config='--psm 6', output_type=pytesseract.Output.DATAFRAME)
            # Filter out empty text detections. Cast to string first to avoid .str accessor errors on numeric/null data.
            data = data[data.text.notna()]
            data['text'] = data['text'].astype(str)
            data = data[data['text'].str.strip() != ""]
            return data
        except Exception as e:
            print(f"OCR Data Error: {e}")
            return None

    def overlay_translation(self, image, provider='google'):
        """
        Translates text in the image and draws the translation over the original.
        """
        try:
            data = self.perform_ocr_with_data(image)
        except Exception as e:
            print(f"OCR Exception: {e}")
            return image, f"OCR Error: {e}"

        if data is None or data.empty:
            return image, ""

        # Group data by line 
        lines = data.groupby(['block_num', 'line_num'])
        
        translated_img = image.copy()
        draw = ImageDraw.Draw(translated_img)
        font_path = utils.get_font_path()
        
        line_data = []
        full_original_text = []

        for _, group in lines:
            line_text = " ".join(group.text.astype(str)).strip()
            if not line_text: continue
            
            full_original_text.append(line_text)
            
            # Save coordinates
            line_data.append({
                'text': line_text,
                'box': (group.left.min(), group.top.min(), (group.left + group.width).max(), (group.top + group.height).max())
            })

        if not line_data:
            return image, ""

        # BATCH TRANSLATION: Join lines with newline
        megatext = "\n".join([item['text'] for item in line_data])
        try:
            translated_megatext = self.translate_text(megatext, provider=provider)
            translated_lines = translated_megatext.split("\n")
        except Exception as e:
            print(f"Translation Exception: {e}")
            return image, f"Translation Error: {e}"

        # Draw results
        for i, item in enumerate(line_data):
            # Align translated lines back to original boxes
            text_to_draw = translated_lines[i] if i < len(translated_lines) else "..."
            
            x_min, y_min, x_max, y_max = item['box']
            box_w = x_max - x_min
            box_h = y_max - y_min
            
            # Draw semi-opaque background for better readability
            # Expand box slightly for padding
            padding = 2
            bg_rect = [x_min - padding, y_min - padding, x_max + padding, y_max + padding]
            draw.rectangle(bg_rect, fill="white")
            
            # Robust font size calculation
            font_size = max(12, int(box_h * 0.9))
            try:
                font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # If text is too wide for the box, shrink it
            text_bbox = draw.textbbox((0, 0), text_to_draw, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            if text_w > box_w and box_w > 0:
                font_size = max(10, int(font_size * (box_w / text_w)))
                try:
                    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
                except:
                    font = ImageFont.load_default()

            draw.text((x_min, y_min), text_to_draw, fill="black", font=font)

        return translated_img, "\n".join(full_original_text)

    def translate_text(self, text, provider='google'):
        # ... (same as before)
        if not text:
            return ""

        if provider == 'openai' and self.openai_client:
            return self._translate_openai(text)
        else:
            return self._translate_google(text)

    def _translate_google(self, text):
        try:
            return self.google_translator.translate(text)
        except Exception as e:
            return f"Google Error: {str(e)[:20]}"

    def _translate_openai(self, text):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate English text to Chinese (Simplified). IMPORTANT: Preserve the number of lines and line breaks exactly as they are in the source text. Do not omit any lines."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"GPT Error: {str(e)[:20]}"
