from deep_translator import GoogleTranslator
from openai import OpenAI
from services.base_translator import BaseTranslator
from utils import helpers as utils

class GoogleTranslatorProvider(BaseTranslator):
    def __init__(self):
        self.translator = GoogleTranslator(source='auto', target='zh-CN')

    def translate(self, text: str) -> str:
        try:
            return self.translator.translate(text)
        except Exception as e:
            return f"Google Error: {str(e)[:20]}"

class OpenAITranslatorProvider(BaseTranslator):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def translate(self, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate English text to Chinese (Simplified). IMPORTANT: Preserve the number of lines and line breaks exactly as they are in the source text. Do not omit any lines."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"GPT Error: {str(e)[:20]}"

class TranslatorFactory:
    @staticmethod
    def get_translator(provider_name: str) -> BaseTranslator:
        if provider_name == 'openai':
            api_key = utils.get_openai_api_key()
            if api_key:
                return OpenAITranslatorProvider(api_key)
            else:
                print("Warning: OpenAI API key not found, falling back to Google.")
        
        return GoogleTranslatorProvider()
