export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-center mb-8">
        Welcome to OmniRAG
      </h1>
      <div className="space-y-4 w-full max-w-md">
        <a
          href="/upload"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Upload Files
        </a>
        <a
          href="/files"
          className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
        >
          List Files
        </a>
        <a
          href="/chat"
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded"
        >
          Chat
        </a>
      </div>
    </div>
  );
}