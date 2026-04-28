import { useState } from 'react';
import { Upload, GitBranch, FileCode, Loader2, CheckCircle, XCircle } from 'lucide-react';
import api from '../api';

interface CodeIngestionProps {
  onIngestionComplete: () => void;
}

interface IngestionResult {
  status: string;
  message?: string;
  chunks_ingested?: number;
  collection_size?: number;
}

function CodeIngestion({ onIngestionComplete }: CodeIngestionProps) {
  const [mode, setMode] = useState<'text' | 'github'>('text');
  const [code, setCode] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [language, setLanguage] = useState('python');
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleIngestText = async () => {
    if (!code.trim()) {
      setError('Please enter some code');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const chunkId = `manual_${Date.now()}`;
      const response = await api.post('/api/ingest', {
        code_chunks: [
          {
            id: chunkId,
            code: code,
            language: language,
            metadata: {
              file_path: fileName || 'manual_input.txt',
              source: 'manual',
              ingested_at: new Date().toISOString(),
            },
          },
        ],
      });

      setResult(response.data);
      setCode('');
      setFileName('');
      onIngestionComplete();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to ingest code');
    } finally {
      setLoading(false);
    }
  };

  const handleIngestGithub = async () => {
    if (!githubUrl.trim()) {
      setError('Please enter a GitHub URL');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/api/ingest', {
        repo_url: githubUrl,
      });

      setResult(response.data);
      setGithubUrl('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to ingest repository');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
      <div className="px-4 py-3 border-b border-zinc-800">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide flex items-center gap-2">
          <Upload className="w-4 h-4" />
          Ingest Code
        </h2>
      </div>

      <div className="p-6 space-y-6">
        {/* Mode Selector */}
        <div className="flex gap-2">
          <button
            onClick={() => setMode('text')}
            className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              mode === 'text'
                ? 'bg-violet-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            <FileCode className="w-4 h-4 inline mr-2" />
            Paste Code
          </button>
          <button
            onClick={() => setMode('github')}
            className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              mode === 'github'
                ? 'bg-violet-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            <GitBranch className="w-4 h-4 inline mr-2" />
            GitHub Repo
          </button>
        </div>

        {/* Text Mode */}
        {mode === 'text' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-300 focus:outline-none focus:ring-2 focus:ring-violet-500"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="java">Java</option>
                  <option value="go">Go</option>
                  <option value="rust">Rust</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-2">
                  File Name (optional)
                </label>
                <input
                  type="text"
                  value={fileName}
                  onChange={(e) => setFileName(e.target.value)}
                  placeholder="example.py"
                  className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">
                Code
              </label>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste your code here..."
                rows={8}
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-300 placeholder-zinc-600 font-mono focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>

            <button
              onClick={handleIngestText}
              disabled={loading}
              className="w-full py-2.5 px-4 bg-violet-600 hover:bg-violet-500 disabled:bg-zinc-700 rounded-lg font-medium transition-all flex items-center justify-center gap-2 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Ingesting...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Ingest Code
                </>
              )}
            </button>
          </div>
        )}

        {/* GitHub Mode */}
        {mode === 'github' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-400 mb-2">
                GitHub Repository URL
              </label>
              <input
                type="text"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/username/repo"
                className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-300 placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>

            <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-xs text-yellow-400">
              <strong>Note:</strong> GitHub ingestion is not yet implemented in the backend. 
              This will clone and process all code files from the repository.
            </div>

            <button
              onClick={handleIngestGithub}
              disabled={loading}
              className="w-full py-2.5 px-4 bg-violet-600 hover:bg-violet-500 disabled:bg-zinc-700 rounded-lg font-medium transition-all flex items-center justify-center gap-2 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Ingesting...
                </>
              ) : (
                <>
                  <GitBranch className="w-4 h-4" />
                  Ingest Repository
                </>
              )}
            </button>
          </div>
        )}

        {/* Success Result */}
        {result && result.status === 'success' && (
          <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-green-400 mb-1">
                Ingestion Successful
              </div>
              <div className="text-xs text-green-400/80">
                {result.chunks_ingested} chunks ingested • Total: {result.collection_size} chunks
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-red-400 mb-1">
                Ingestion Failed
              </div>
              <div className="text-xs text-red-400/80">{error}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CodeIngestion;
