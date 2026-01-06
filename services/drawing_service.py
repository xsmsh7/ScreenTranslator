from PIL import ImageDraw, ImageFont
from utils import helpers as utils

def draw_translation_overlay(image, lines_metadata, translated_texts):
    """
    Draws translated text onto the image using a two-pass rendering approach.
    Pass 1: Draw all background rectangles.
    Pass 2: Draw all text.
    """
    draw = ImageDraw.Draw(image)
    font_path = utils.get_font_path()
    
    # PASS 1: Draw all background "patches"
    for metadata in lines_metadata:
        x_min, y_min, x_max, y_max = metadata['box']
        draw.rectangle([x_min-2, y_min-2, x_max+2, y_max+2], fill="white")

    # PASS 2: Draw all translated text on top of the patches
    for i, metadata in enumerate(lines_metadata):
        if i >= len(translated_texts): break
        
        x_min, y_min, x_max, y_max = metadata['box']
        box_w = x_max - x_min
        box_h = y_max - y_min
        
        translated_text = translated_texts[i].strip()
        
        # Robust font size calculation
        font_size = max(12, int(box_h * 0.9))
        try:
            font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Auto-shrink logic
        text_bbox = draw.textbbox((0, 0), translated_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        if text_w > box_w and box_w > 0:
            font_size = max(10, int(font_size * (box_w / text_w)))
            try:
                font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
            except:
                font = ImageFont.load_default()

        draw.text((x_min, y_min), translated_text, fill="black", font=font)
