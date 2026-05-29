import { useState } from 'react';

interface Citation {
  text: string;
  source: string;
  page?: number | null;
  timestamp?: number | null;
  score: number;
}

interface ChatResponse {
  response: string;
  citations: Citation[];
  confidence: string;
}

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setChatResponse(null);

    try {
      const res = await fetch('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (res.ok) {
        const data: ChatResponse = await res.json();
        setChatResponse(data);
      } else {
        throw new Error('Chat request failed');
      }
    } catch (err) {
      setChatResponse({
        response: 'Error: Failed to get response from the agent.',
        citations: [],
        confidence: 'low',
      });
    } finally {
      setLoading(false);
    }
  };

  const confidenceColor = (c: string) => {
    if (c === 'high') return 'text-green-600';
    if (c === 'medium') return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="w-full max-w-2xl space-y-4">
      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your uploaded documents..."
          className="w-full border border-gray-300 rounded p-2 h-24 resize-none"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Send'}
        </button>
      </form>

      {chatResponse && (
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded">
            <div className="flex items-center gap-2 mb-2">
              <span className="font-medium">Response</span>
              <span className={`text-xs px-2 py-0.5 rounded-full bg-gray-200 ${confidenceColor(chatResponse.confidence)}`}>
                {chatResponse.confidence} confidence
              </span>
            </div>
            <pre className="mt-2 whitespace-pre-wrap font-sans text-sm">{chatResponse.response}</pre>
          </div>

          {chatResponse.citations.length > 0 && (
            <div className="p-4 border border-gray-200 rounded">
              <p className="font-medium text-sm mb-2">Sources</p>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {chatResponse.citations.map((c, i) => (
                  <div key={i} className="text-xs p-2 bg-gray-50 rounded border border-gray-100">
                    <div className="flex items-center gap-2 mb-1 text-gray-500">
                      <span className="font-medium">{c.source}</span>
                      {c.page && <span>Page {c.page}</span>}
                      {c.timestamp != null && <span>@{c.timestamp.toFixed(1)}s</span>}
                      <span className="ml-auto">Score: {(c.score * 100).toFixed(0)}%</span>
                    </div>
                    <p className="text-gray-700">{c.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatInterface;