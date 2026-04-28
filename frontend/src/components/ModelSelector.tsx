import { type Model } from '../api';
import { Sparkles } from 'lucide-react';

interface ModelSelectorProps {
  models: Model[];
  selectedModel: string;
  onChange: (model: string) => void;
}

function ModelSelector({ models, selectedModel, onChange }: ModelSelectorProps) {
  if (models.length === 0) {
    return (
      <div className="text-sm text-zinc-500">
        Loading models...
      </div>
    );
  }

  const selected = models.find(m => m.id === selectedModel);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-zinc-400">
        Claude Model
      </label>
      <div className="relative">
        <select
          value={selectedModel}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-sm text-zinc-200 focus:outline-none focus:ring-2 focus:ring-violet-500 appearance-none cursor-pointer"
        >
          {models.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name} - {model.cost}
            </option>
          ))}
        </select>
        <Sparkles className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />
      </div>
      {selected && (
        <div className="flex items-center gap-4 text-xs text-zinc-500">
          {selected.quality && (
            <span>Quality: {selected.quality}</span>
          )}
          {selected.description && (
            <span>{selected.description}</span>
          )}
        </div>
      )}
    </div>
  );
}

export default ModelSelector;
