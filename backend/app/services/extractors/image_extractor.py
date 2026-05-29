from pathlib import Path
from typing import List, Dict, Any

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


def extract_image(file_path: str) -> List[Dict[str, Any]]:
    filename = Path(file_path).name
    if not HAS_OCR:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'image',
                'error': 'OCR dependencies not installed (pillow/pytesseract)'
            }
        }]
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        caption = _generate_caption(text, filename)
        return [{
            'text': text.strip(),
            'metadata': {
                'source': filename,
                'type': 'image',
                'caption': caption,
                'image_size': f"{img.width}x{img.height}",
                'image_mode': img.mode
            }
        }]
    except Exception as e:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'image',
                'error': str(e)
            }
        }]


def _generate_caption(ocr_text: str, filename: str) -> str:
    if not ocr_text.strip():
        return f"Image with no detectable text"
    words = ocr_text.strip().split()
    preview = ' '.join(words[:15])
    return f"Image containing text: {preview}{'...' if len(words) > 15 else ''}"
