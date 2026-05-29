const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface FileItem {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  upload_time: string;
}

export interface Citation {
  text: string;
  source: string;
  page?: number | null;
  timestamp?: number | null;
  score: number;
  chunk_index?: number | null;
}

export interface ChatResponse {
  response: string;
  citations: Citation[];
  confidence: string;
}

export interface IngestionResult {
  file_id: string;
  filename: string;
  chunks_count: number;
  status: string;
  error?: string | null;
}

export async function uploadFile(file: File): Promise<IngestionResult> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/upload/`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || 'Upload failed');
  }
  return res.json();
}

export async function getFiles(): Promise<FileItem[]> {
  const res = await fetch(`${API_BASE}/files/`);
  if (!res.ok) throw new Error('Failed to fetch files');
  return res.json();
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || 'Chat request failed');
  }
  return res.json();
}
