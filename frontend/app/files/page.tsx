import { useEffect, useState } from 'react';
import FileList from '@/components/FileList';

export default function FilesPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold mb-6">Uploaded Files</h1>
      <FileList />
      <a href="/" className="mt-4 text-blue-600 hover:underline">
        Back to Home
      </a>
    </div>
  );
}