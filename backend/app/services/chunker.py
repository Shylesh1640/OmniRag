from typing import List, Dict, Any


def chunk_document(
    extracted_data: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    chunks = []
    for entry in extracted_data:
        text = entry.get('text', '')
        metadata = entry.get('metadata', {})
        if not text:
            chunks.append({
                'text': '',
                'chunk_index': 0,
                'metadata': {**metadata, 'error': 'No text content'}
            })
            continue
        text_chunks = _split_text(text, chunk_size, chunk_overlap)
        for i, chunk_text in enumerate(text_chunks):
            chunks.append({
                'text': chunk_text,
                'chunk_index': i,
                'metadata': {
                    **metadata,
                    'num_chunks': len(text_chunks)
                }
            })
    return chunks


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = end - chunk_overlap
    return chunks
