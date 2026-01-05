import pytesseract
from deep_translator import GoogleTranslator
from openai import OpenAI
import utils

# Set tesseract cmd
pytesseract.pytesseract.tesseract_cmd = utils.get_tesseract_cmd()

class TranslatorService:
    def __init__(self):
        self.google_translator = GoogleTranslator(source='auto', target='zh-CN')
        self.openai_client = None
        
        api_key = utils.get_openai_api_key()
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)

    def perform_ocr(self, image):
        """
        Extracts text from a PIL Image using Tesseract OCR.
        """
        try:
            # Adding configuration for better accuracy
            # --psm 6: Assume a single uniform block of text.
            text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
            return text.strip()
        except Exception as e:
            return f"Error during OCR: {str(e)}"

    def translate_text(self, text, provider='google'):
        """
        Translates text to Chinese using the specified provider.
        """
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
            return f"Google Translation Error: {str(e)}"

    def _translate_openai(self, text):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful translator. Translate the following English text to Chinese (Simplified). Only return the translated text."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI Translation Error: {str(e)}"
