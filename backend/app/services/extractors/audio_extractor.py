from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

_whisper_model = None


def _get_whisper_model(model_size: str = "base"):
    global _whisper_model
    if _whisper_model is None and HAS_WHISPER:
        _whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _whisper_model


def extract_audio(file_path: str, model_size: str = "base") -> List[Dict[str, Any]]:
    filename = Path(file_path).name
    if not HAS_WHISPER:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'audio',
                'error': 'faster-whisper not installed'
            }
        }]
    try:
        model = _get_whisper_model(model_size)
        if model is None:
            return [{
                'text': '',
                'metadata': {
                    'source': filename,
                    'type': 'audio',
                    'error': 'Failed to load Whisper model'
                }
            }]
        segments, info = model.transcribe(file_path, beam_size=5)
        results = []
        for segment in segments:
            results.append({
                'text': segment.text.strip(),
                'metadata': {
                    'source': filename,
                    'type': 'audio',
                    'start': segment.start,
                    'end': segment.end,
                    'language': info.language,
                    'language_probability': info.language_probability
                }
            })
        if not results:
            results.append({
                'text': '',
                'metadata': {
                    'source': filename,
                    'type': 'audio',
                    'error': 'No speech detected'
                }
            })
        return results
    except Exception as e:
        return [{
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'audio',
                'error': str(e)
            }
        }]
