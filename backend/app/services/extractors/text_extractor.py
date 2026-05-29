from pathlib import Path
from typing import List, Dict, Any

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


def extract_text(file_path: str) -> List[Dict[str, Any]]:
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        return extract_pdf(file_path)
    else:
        return extract_plain_text(file_path)


def extract_plain_text(file_path: str) -> List[Dict[str, Any]]:
    filename = Path(file_path).name
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        return [{
            'text': text,
            'metadata': {
                'source': filename,
                'page': 1,
                'type': 'text'
            }
        }]
    except Exception as e:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'text',
                'error': str(e)
            }
        }]


def extract_pdf(file_path: str) -> List[Dict[str, Any]]:
    filename = Path(file_path).name
    if not HAS_PDF:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'pdf',
                'error': 'PyPDF2 not installed'
            }
        }]
    try:
        pages = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        'text': text.strip(),
                        'metadata': {
                            'source': filename,
                            'page': i,
                            'total_pages': len(reader.pages),
                            'type': 'pdf'
                        }
                    })
        if not pages:
            pages.append({
                'text': '',
                'metadata': {
                    'source': filename,
                    'page': 1,
                    'type': 'pdf',
                    'error': 'No text could be extracted'
                }
            })
        return pages
    except Exception as e:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'pdf',
                'error': str(e)
            }
        }]
