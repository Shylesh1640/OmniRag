import { useState } from 'react';

interface IngestionResult {
  file_id: string;
  filename: string;
  chunks_count: number;
  status: string;
  error?: string | null;
}

const statusLabel: Record<string, string> = {
  success: 'Ingested successfully',
  partial: 'Partially ingested',
  failed: 'Ingestion failed',
};

const statusColor: Record<string, string> = {
  success: 'text-green-600',
  partial: 'text-yellow-600',
  failed: 'text-red-600',
};

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<IngestionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setResult(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/v1/upload/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data: IngestionResult = await response.json();
        setResult(data);
      } else {
        const text = await response.text();
        throw new Error(text || 'Upload failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-4">
      <input
        type="file"
        onChange={handleFileChange}
        className="w-full border border-gray-300 rounded p-2"
        disabled={uploading}
      />
      {selectedFile && (
        <div>
          <p className="text-sm text-gray-600">Selected: {selectedFile.name}</p>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 mt-2"
          >
            {uploading ? 'Processing...' : 'Upload & Ingest'}
          </button>
        </div>
      )}
      {result && (
        <div className="p-3 border border-gray-200 rounded space-y-1 text-sm">
          <p className={statusColor[result.status] || 'text-gray-600'}>
            {statusLabel[result.status] || result.status}
          </p>
          <p>Chunks created: {result.chunks_count}</p>
          {result.error && <p className="text-red-500">Error: {result.error}</p>}
        </div>
      )}
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  );
};

export default FileUploader;