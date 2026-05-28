import { useState } from 'react';

const FileUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploadStatus('Uploading...');
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/v1/upload/', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`Upload successful! File ID: ${result.id}`);
        setUploadProgress(100);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.');
      setUploadProgress(0);
    }
  };

  return (
    <div className="w-full max-w-md space-y-4">
      <input
        type="file"
        onChange={handleFileChange}
        className="w-full border border-gray-300 rounded p-2"
      />
      {selectedFile && (
        <div>
          <p>Selected file: {selectedFile.name}</p>
          <button
            onClick={handleUpload}
            disabled={uploadProgress === 100}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            {uploadProgress === 100 ? 'Uploaded' : 'Upload File'}
          </button>
        </div>
      )}
      <div className="mt-2">
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="bg-blue-600 h-2.5 rounded-full"
            style={{ width: uploadProgress + '%' }}
          ></div>
        </div>
        <p className="mt-1 text-center">{uploadStatus}</p>
      </div>
    </div>
  );
};

export default FileUploader;