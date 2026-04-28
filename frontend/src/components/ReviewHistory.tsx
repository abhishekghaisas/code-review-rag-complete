import { useState, useEffect } from 'react';
import { Clock, Trash2, Eye, Calendar } from 'lucide-react';
import type { ReviewResponse } from '../api';

interface HistoryItem {
  id: string;
  timestamp: string;
  code: string;
  language: string;
  model: string;
  review: ReviewResponse;
}

interface ReviewHistoryProps {
  onLoadReview: (item: HistoryItem) => void;
}

function ReviewHistory({ onLoadReview }: ReviewHistoryProps) {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    const saved = localStorage.getItem('review_history');
    if (saved) {
      setHistory(JSON.parse(saved));
    }
  };

  const saveToHistory = (code: string, language: string, model: string, review: ReviewResponse) => {
    const item: HistoryItem = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      code,
      language,
      model,
      review,
    };

    const updated = [item, ...history].slice(0, 20); // Keep last 20
    setHistory(updated);
    localStorage.setItem('review_history', JSON.stringify(updated));
  };

  const deleteItem = (id: string) => {
    const updated = history.filter((item) => item.id !== id);
    setHistory(updated);
    localStorage.setItem('review_history', JSON.stringify(updated));
  };

  const clearHistory = () => {
    if (confirm('Are you sure you want to clear all history?')) {
      setHistory([]);
      localStorage.removeItem('review_history');
    }
  };

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const getCodePreview = (code: string) => {
    const lines = code.split('\n');
    return lines[0].substring(0, 50) + (lines[0].length > 50 || lines.length > 1 ? '...' : '');
  };

  // Expose saveToHistory function
  useEffect(() => {
    (window as any).saveReviewToHistory = saveToHistory;
  }, [history]);

  if (history.length === 0) {
    return (
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-8">
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center">
            <Clock className="w-8 h-8 text-zinc-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-zinc-300 mb-2">No History Yet</h3>
            <p className="text-sm text-zinc-500">
              Your code reviews will appear here once you start reviewing
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide flex items-center gap-2">
          <Clock className="w-4 h-4" />
          Review History ({history.length})
        </h2>
        <button
          onClick={clearHistory}
          className="text-xs text-zinc-500 hover:text-red-400 transition-colors"
        >
          Clear All
        </button>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {history.map((item) => (
          <div
            key={item.id}
            className={`p-4 border-b border-zinc-800 hover:bg-zinc-800/50 transition-colors ${
              selectedId === item.id ? 'bg-zinc-800/50' : ''
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono text-violet-400">{item.language}</span>
                  <span className="text-xs text-zinc-600">•</span>
                  <span className="text-xs text-zinc-500">{formatDate(item.timestamp)}</span>
                </div>
                <div className="text-sm text-zinc-300 font-mono mb-2 truncate">
                  {getCodePreview(item.code)}
                </div>
                <div className="text-xs text-zinc-500">
                  Model: {item.review.model_used}
                  {item.review.rag_enabled && (
                    <span className="ml-2 text-green-400">• RAG enabled</span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setSelectedId(item.id);
                    onLoadReview(item);
                  }}
                  className="p-2 hover:bg-zinc-700 rounded-lg transition-colors"
                  title="Load review"
                >
                  <Eye className="w-4 h-4 text-zinc-400" />
                </button>
                <button
                  onClick={() => deleteItem(item.id)}
                  className="p-2 hover:bg-zinc-700 rounded-lg transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4 text-zinc-400 hover:text-red-400" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ReviewHistory;
export type { HistoryItem };
