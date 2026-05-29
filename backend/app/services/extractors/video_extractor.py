import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from app.services.extractors.audio_extractor import extract_audio

try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


def extract_video(
    file_path: str,
    frame_interval: int = 30,
    whisper_model_size: str = "base"
) -> List[Dict[str, Any]]:
    filename = Path(file_path).name
    transcript = _extract_video_audio(file_path, filename, whisper_model_size)
    frames = _extract_video_frames(file_path, filename, frame_interval)
    return _combine_video_results(transcript, frames, filename)


def _extract_video_audio(
    file_path: str,
    filename: str,
    model_size: str
) -> List[Dict[str, Any]]:
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_path = tmp.name
    try:
        subprocess.run(
            ['ffmpeg', '-i', file_path,
             '-vn', '-acodec', 'pcm_s16le',
             '-ar', '16000', '-ac', '1',
             '-y', audio_path],
            capture_output=True, timeout=300
        )
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            return [{
                'text': '',
                'metadata': {
                    'source': filename, 'type': 'video_transcript',
                    'error': 'Audio extraction produced empty file'
                }
            }]
        segments = extract_audio(audio_path, model_size)
        for seg in segments:
            seg['metadata']['type'] = 'video_transcript'
        return segments
    except subprocess.TimeoutExpired:
        return [{
            'text': '', 'metadata': {
                'source': filename, 'type': 'video_transcript',
                'error': 'Audio extraction timed out'
            }
        }]
    except FileNotFoundError:
        return [{
            'text': '', 'metadata': {
                'source': filename, 'type': 'video_transcript',
                'error': 'ffmpeg not found on system'
            }
        }]
    except Exception as e:
        return [{
            'text': '', 'metadata': {
                'source': filename, 'type': 'video_transcript',
                'error': str(e)
            }
        }]
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


def _extract_video_frames(
    file_path: str,
    filename: str,
    interval: int
) -> List[Dict[str, Any]]:
    if not HAS_OPENCV:
        return [{
            'text': '', 'metadata': {
                'source': filename, 'type': 'video_frame',
                'error': 'OpenCV not installed'
            }
        }]
    frames = []
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return [{
            'text': '', 'metadata': {
                'source': filename, 'type': 'video_frame',
                'error': 'Could not open video file'
            }
        }]
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            current_time = frame_count / fps if fps > 0 else 0
            if int(current_time) % interval == 0 and current_time > 0:
                ocr_text = _ocr_frame(frame)
                if ocr_text:
                    frames.append({
                        'text': ocr_text,
                        'metadata': {
                            'source': filename,
                            'type': 'video_frame',
                            'timestamp': current_time,
                            'frame_number': frame_count,
                            'duration': duration
                        }
                    })
            frame_count += 1
        cap.release()
        if not frames:
            cap = cv2.VideoCapture(file_path)
            ret, frame = cap.read()
            if ret:
                ocr_text = _ocr_frame(frame)
                if ocr_text:
                    frames.append({
                        'text': ocr_text,
                        'metadata': {
                            'source': filename, 'type': 'video_frame',
                            'timestamp': 0.0, 'frame_number': 0,
                            'duration': duration
                        }
                    })
            cap.release()
        return frames
    except Exception as e:
        cap.release()
        return [{
            'text': '', 'metadata': {
                'source': filename, 'type': 'video_frame',
                'error': str(e)
            }
        }]


def _ocr_frame(frame) -> str:
    if not HAS_OCR:
        return ''
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        text = pytesseract.image_to_string(pil_img)
        return text.strip()
    except Exception:
        return ''


def _combine_video_results(
    transcript: List[Dict[str, Any]],
    frames: List[Dict[str, Any]],
    filename: str
) -> List[Dict[str, Any]]:
    combined = []
    transcript_text = ' '.join(
        seg['text'] for seg in transcript if seg.get('text')
    )
    if transcript_text:
        combined.append({
            'text': transcript_text,
            'metadata': {
                'source': filename,
                'type': 'video_combined',
                'segments_count': len(transcript),
                'frame_count': len(frames)
            }
        })
    for frame in frames:
        if frame.get('text'):
            combined.append({
                'text': frame['text'],
                'metadata': frame['metadata']
            })
    if not combined:
        combined.append({
            'text': '',
            'metadata': {
                'source': filename,
                'type': 'video_combined',
                'error': 'No content could be extracted from video'
            }
        })
    return combined
