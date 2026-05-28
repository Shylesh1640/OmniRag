import { useEffect, useState } from 'react';

const FileList = () => {
  const [files, setFiles] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/files/');
        if (!response.ok) {
          throw new Error('Failed to fetch files');
        }
        const result = await response.json();
        setFiles(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  if (loading) return <p>Loading files...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  return (
    <div className="w-full max-w-md space-y-4">
      {files.length === 0 ? (
        <p>No files uploaded yet.</p>
      ) : (
        <ul className="space-y-2">
          {files.map((file: any) => (
            <li key={file.id} className="p-2 border border-gray-200 rounded">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">{file.filename}</p>
                  <p className="text-sm text-gray-500">
                    {file.content_type} • {Math.round(file.size / 1024)} KB
                  </p>
                </div>
                <p className="text-sm text-gray-400">
                  Uploaded: {new Date(file.upload_time).toLocaleString()}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default FileList;