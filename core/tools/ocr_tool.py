"""
OCR tool for extracting text from images.
"""
import pytesseract
from PIL import Image
import easyocr
import io

class OCRTool:
    """
    OCR tool for extracting text from images using pytesseract and EasyOCR fallback.
    """
    def __init__(self):
        self.reader = None
    
    def extract_text(self, uploaded_file):
        """
        Extract text from a Streamlit uploaded file (image) using pytesseract, fallback to EasyOCR.
        """
        try:
            image_bytes = uploaded_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            if text.strip():
                return text
        except Exception:
            pass
        # Fallback to EasyOCR
        try:
            if self.reader is None:
                self.reader = easyocr.Reader(['en'])
            result = self.reader.readtext(image_bytes, detail=0, paragraph=True)
            return '\n'.join(result)
        except Exception:
            return "[OCR failed]"

def extract_from_image(image_bytes):
    """
    Legacy function for backward compatibility.
    """
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