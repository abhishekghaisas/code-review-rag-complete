import { Database, RefreshCw } from 'lucide-react';

interface StatsPanelProps {
  stats: {
    collection_name: string;
    total_chunks: number;
    embedding_model: string;
    embedding_dimension: number;
  };
  onRefresh: () => void;
}

function StatsPanel({ stats, onRefresh }: StatsPanelProps) {
  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide flex items-center gap-2">
          <Database className="w-4 h-4" />
          Vector Database
        </h2>
        <button
          onClick={onRefresh}
          className="p-1 hover:bg-zinc-800 rounded transition-colors"
          title="Refresh stats"
        >
          <RefreshCw className="w-4 h-4 text-zinc-500" />
        </button>
      </div>
      <div className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-2xl font-bold text-violet-400">
              {stats.total_chunks}
            </div>
            <div className="text-xs text-zinc-500">Code Chunks</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-fuchsia-400">
              {stats.embedding_dimension}
            </div>
            <div className="text-xs text-zinc-500">Dimensions</div>
          </div>
        </div>
        
        <div className="pt-4 border-t border-zinc-800 space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-zinc-500">Collection</span>
            <span className="text-zinc-400 font-mono">{stats.collection_name}</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-zinc-500">Model</span>
            <span className="text-zinc-400 font-mono">{stats.embedding_model}</span>
          </div>
        </div>

        {stats.total_chunks === 0 && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400 text-xs">
            No code ingested yet. Use the API to add code chunks for RAG.
          </div>
        )}
      </div>
    </div>
  );
}

export default StatsPanel;
