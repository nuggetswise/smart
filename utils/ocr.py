import pytesseract
from PIL import Image
import easyocr
import io

def extract_text(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        if text.strip():
            return text
    except Exception:
        pass
    # Fallback to EasyOCR
    try:
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_bytes, detail=0, paragraph=True)
        return '\n'.join(result)
    except Exception:
        return "[OCR failed]" 