import asyncio
import pandas as pd
from PIL import Image
import winsdk.windows.media.ocr as ocr
import winsdk.windows.graphics.imaging as imaging
import winsdk.windows.storage.streams as streams
from winsdk.windows.globalization import Language

class WindowsOCR:
    def __init__(self):
        self.engine = ocr.OcrEngine.try_create_from_user_profile_languages()
        if not self.engine:
            # Fallback for systems with non-standard locales, force English
            self.engine = ocr.OcrEngine.try_create_from_language(Language("en-US"))
            
    def perform_ocr(self, image: Image.Image) -> pd.DataFrame:
        """
        Executes Windows Native OCR and returns a DataFrame compatible with Tesseract output.
        Required Columns: ['text', 'left', 'top', 'width', 'height', 'conf', 'block_num', 'line_num']
        """
        try:
            # Convert PIL Image to SoftwareBitmap
            # Windows OCR requires BGRA8 or similar
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            # Create SoftwareBitmap from bytes
            width, height = image.size
            if width == 0 or height == 0:
                return None
                
            pixel_data = image.tobytes("raw", "BGRA")
            
            # Use raw buffer to create bitmap
            # We need to run the async OCR operation
            result = asyncio.run(self._recognize_async(pixel_data, width, height))
            
            if not result:
                return pd.DataFrame()
            
            # Parse results into DataFrame
            data_list = []
            
            # Windows OCR structure: Result -> Lines -> Words
            # We map Line Index -> line_num
            # We map 1 -> block_num (Windows OCR doesn't strictly provide blocks like Tesseract)
            
            for line_idx, line in enumerate(result.lines):
                for word in line.words:
                    bbox = word.bounding_rect
                    data_list.append({
                        'text': word.text,
                        'left': int(bbox.x),
                        'top': int(bbox.y),
                        'width': int(bbox.width),
                        'height': int(bbox.height),
                        'conf': 100, # Windows OCR doesn't expose confidence per word easily, assume High
                        'block_num': 1,
                        'line_num': line_idx + 1
                    })
            
            df = pd.DataFrame(data_list)
            return df
            
        except Exception as e:
            print(f"Windows OCR Error: {e}")
            return None

    async def _recognize_async(self, pixel_data, width, height):
        # Create DataWriter to write bytes to IBuffer
        writer = streams.DataWriter(streams.InMemoryRandomAccessStream())
        # pixel_data is already bytes, no need to convert to list (which causes error)
        writer.write_bytes(pixel_data)
        
        # In a real scenario creating SoftwareBitmap from bytes in Python with winsdk can be tricky
        # A more robust way might be valid, but let's try the direct SoftwareBitmap approach if possible.
        # Alternatively, saving to temp file is safer but slower. 
        # Let's try to simple logic: SoftwareBitmap.create_copy_from_buffer
        
        # Quickest stable way in Python winsdk without complex buffer mapping:
        # Create a SoftwareBitmap directly? 
        # Actually imaging.SoftwareBitmap.create_copy_from_buffer requires an IBuffer.
        # writer.detach_buffer() returns the buffer.
        
        ibuffer = writer.detach_buffer()
        bitmap = imaging.SoftwareBitmap.create_copy_from_buffer(
            ibuffer, 
            imaging.BitmapPixelFormat.BGRA8, 
            width, 
            height
        )
        
        return await self.engine.recognize_async(bitmap)
