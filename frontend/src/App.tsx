import { useState, useEffect } from 'react';
import CodeEditor from './components/CodeEditor';
import ReviewPanel from './components/ReviewPanel';
import ModelSelector from './components/ModelSelector';
import StatsPanel from './components/StatsPanel';
import CodeIngestion from './components/CodeIngestion';
import ReviewHistory, { type HistoryItem } from './components/ReviewHistory';
import ComparisonMode from './components/ComparisonMode';
import ExportReview from './components/ExportReview';
import { ToastContainer } from './components/Toast';
import { reviewCode, getModels, getStats, type ReviewResponse, type Model } from './api';
import { Code2, Sparkles, Database, Upload, Clock, GitCompare, Save } from 'lucide-react';

const SAMPLE_CODE = `def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total`;

type TabType = 'review' | 'compare' | 'ingest' | 'history';

interface Toast {
  id: string;
  message: string;
  type?: 'success' | 'error' | 'info';
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('review');
  const [code, setCode] = useState(SAMPLE_CODE);
  const [language, setLanguage] = useState('python');
  const [selectedModel, setSelectedModel] = useState('claude-haiku-4-5-20251001');
  const [useRag, setUseRag] = useState(true);
  const [models, setModels] = useState<Model[]>([]);
  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [lastSavedId, setLastSavedId] = useState<number | null>(null);

  useEffect(() => {
    loadModels();
    loadStats();
  }, []);

  const loadModels = async () => {
    try {
      const data = await getModels();
      setModels(data.models);
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  };

  const loadStats = async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, message, type }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleReview = async () => {
    if (!code.trim()) {
      setError('Please enter some code to review');
      return;
    }

    setLoading(true);
    setError(null);
    setReview(null);
    setLastSavedId(null);

    try {
      const result = await reviewCode({
        code,
        language,
        model: selectedModel,
        use_rag: useRag,
        n_similar: 3,
      });
      setReview(result);
      
      // Show save confirmation
      if (result.id) {
        setLastSavedId(result.id);
        showToast(`Review saved to database (ID: ${result.id})`, 'success');
      }
      
      // Also save to localStorage for history component
      if ((window as any).saveReviewToHistory) {
        (window as any).saveReviewToHistory(code, language, selectedModel, result);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to generate review';
      setError(errorMsg);
      showToast(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadHistory = (item: HistoryItem) => {
    setCode(item.code);
    setLanguage(item.language);
    setSelectedModel(item.model);
    setReview(item.review);
    setActiveTab('review');
    showToast('Review loaded from history', 'info');
  };

  const tabs = [
    { id: 'review' as TabType, label: 'Review', icon: Sparkles },
    { id: 'compare' as TabType, label: 'Compare', icon: GitCompare },
    { id: 'ingest' as TabType, label: 'Ingest', icon: Upload },
    { id: 'history' as TabType, label: 'History', icon: Clock },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-fuchsia-500 rounded-lg flex items-center justify-center">
                <Code2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
                  Code Review RAG
                </h1>
                <p className="text-xs text-zinc-500">AI-powered with Claude</p>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              {lastSavedId && (
                <div className="flex items-center gap-2 text-sm bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-1.5">
                  <Save className="w-4 h-4 text-green-400" />
                  <span className="text-green-400">Saved (ID: {lastSavedId})</span>
                </div>
              )}
              {stats && (
                <div className="flex items-center gap-2 text-sm">
                  <Database className="w-4 h-4 text-violet-400" />
                  <span className="text-zinc-400">
                    {stats.total_chunks} chunks indexed
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-zinc-800 bg-zinc-900/30">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium transition-all flex items-center gap-2 border-b-2 ${
                    activeTab === tab.id
                      ? 'border-violet-500 text-violet-400'
                      : 'border-transparent text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Review Tab */}
        {activeTab === 'review' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Panel - Editor */}
            <div className="space-y-6">
              {/* Controls */}
              <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">
                    Configuration
                  </h2>
                </div>

                <ModelSelector
                  models={models}
                  selectedModel={selectedModel}
                  onChange={setSelectedModel}
                />

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useRag}
                      onChange={(e) => setUseRag(e.target.checked)}
                      className="w-4 h-4 rounded bg-zinc-800 border-zinc-700 text-violet-500 focus:ring-violet-500 focus:ring-offset-0"
                    />
                    <span className="text-sm text-zinc-300">
                      Use RAG (similarity search)
                    </span>
                  </label>

                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="px-3 py-1.5 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="typescript">TypeScript</option>
                    <option value="java">Java</option>
                    <option value="go">Go</option>
                    <option value="rust">Rust</option>
                  </select>
                </div>

                <button
                  onClick={handleReview}
                  disabled={loading}
                  className="w-full py-3 px-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:from-zinc-700 disabled:to-zinc-700 rounded-lg font-medium transition-all flex items-center justify-center gap-2 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                      Reviewing & Saving...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Review Code
                    </>
                  )}
                </button>

                {error && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {error}
                  </div>
                )}
              </div>

              {/* Code Editor */}
              <CodeEditor
                value={code}
                onChange={setCode}
                language={language}
              />
            </div>

            {/* Right Panel - Review Results */}
            <div className="space-y-6">
              <ReviewPanel review={review} loading={loading} />
              {review && <ExportReview code={code} language={language} review={review} />}
              {stats && <StatsPanel stats={stats} onRefresh={loadStats} />}
            </div>
          </div>
        )}

        {/* Compare Tab */}
        {activeTab === 'compare' && (
          <div className="space-y-6">
            <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6">
              <CodeEditor value={code} onChange={setCode} language={language} />
            </div>
            <ComparisonMode code={code} language={language} models={models} useRag={useRag} />
          </div>
        )}

        {/* Ingest Tab */}
        {activeTab === 'ingest' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CodeIngestion 
              onIngestionComplete={() => {
                loadStats();
                showToast('Code ingested successfully!', 'success');
              }} 
            />
            {stats && <StatsPanel stats={stats} onRefresh={loadStats} />}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <ReviewHistory onLoadReview={handleLoadHistory} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-800 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <p className="text-center text-sm text-zinc-500">
            Built with FastAPI, ChromaDB, and Anthropic Claude • RAG-powered code review
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;