import { useState } from 'react';
import { GitCompare, Loader2, Sparkles } from 'lucide-react';
import { reviewCode, type Model, type ReviewResponse } from '../api';
import ReactMarkdown from 'react-markdown';

interface ComparisonModeProps {
  code: string;
  language: string;
  models: Model[];
  useRag: boolean;
}

interface ComparisonResult {
  model: string;
  modelName: string;
  review: ReviewResponse | null;
  loading: boolean;
  error: string | null;
}

function ComparisonMode({ code, language, models, useRag }: ComparisonModeProps) {
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [results, setResults] = useState<ComparisonResult[]>([]);
  const [comparing, setComparing] = useState(false);

  const toggleModel = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      setSelectedModels(selectedModels.filter((m) => m !== modelId));
    } else {
      if (selectedModels.length < 3) {
        setSelectedModels([...selectedModels, modelId]);
      }
    }
  };

  const handleCompare = async () => {
    if (!code.trim()) {
      alert('Please enter some code to review');
      return;
    }

    if (selectedModels.length < 2) {
      alert('Please select at least 2 models to compare');
      return;
    }

    setComparing(true);
    const initialResults: ComparisonResult[] = selectedModels.map((modelId) => ({
      model: modelId,
      modelName: models.find((m) => m.id === modelId)?.name || modelId,
      review: null,
      loading: true,
      error: null,
    }));

    setResults(initialResults);

    // Run reviews in parallel
    const promises = selectedModels.map(async (modelId, index) => {
      try {
        const result = await reviewCode({
          code,
          language,
          model: modelId,
          use_rag: useRag,
          n_similar: 3,
        });

        setResults((prev) => {
          const updated = [...prev];
          updated[index] = {
            ...updated[index],
            review: result,
            loading: false,
          };
          return updated;
        });
      } catch (err: any) {
        setResults((prev) => {
          const updated = [...prev];
          updated[index] = {
            ...updated[index],
            error: err.response?.data?.detail || 'Failed to generate review',
            loading: false,
          };
          return updated;
        });
      }
    });

    await Promise.all(promises);
    setComparing(false);
  };

  return (
    <div className="space-y-6">
      {/* Model Selection */}
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide flex items-center gap-2">
            <GitCompare className="w-4 h-4" />
            Compare Models
          </h2>
          <span className="text-xs text-zinc-500">
            Select 2-3 models ({selectedModels.length}/3)
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => toggleModel(model.id)}
              disabled={!selectedModels.includes(model.id) && selectedModels.length >= 3}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                selectedModels.includes(model.id)
                  ? 'border-violet-500 bg-violet-500/10'
                  : 'border-zinc-800 bg-zinc-800/50 hover:border-zinc-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="text-sm font-medium text-zinc-200">{model.name}</div>
                {selectedModels.includes(model.id) && (
                  <div className="w-5 h-5 bg-violet-500 rounded-full flex items-center justify-center">
                    <span className="text-xs text-white">✓</span>
                  </div>
                )}
              </div>
              <div className="text-xs text-zinc-500">{model.cost}</div>
              {model.quality && (
                <div className="text-xs text-zinc-600 mt-1">Quality: {model.quality}</div>
              )}
            </button>
          ))}
        </div>

        <button
          onClick={handleCompare}
          disabled={comparing || selectedModels.length < 2}
          className="w-full py-3 px-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 disabled:from-zinc-700 disabled:to-zinc-700 rounded-lg font-medium transition-all flex items-center justify-center gap-2 disabled:cursor-not-allowed"
        >
          {comparing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Comparing...
            </>
          ) : (
            <>
              <GitCompare className="w-4 h-4" />
              Compare Selected Models
            </>
          )}
        </button>
      </div>

      {/* Comparison Results */}
      {results.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {results.map((result, index) => (
            <div key={index} className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
              <div className="px-4 py-3 border-b border-zinc-800 bg-zinc-950">
                <h3 className="text-sm font-semibold text-zinc-300">{result.modelName}</h3>
                <p className="text-xs text-zinc-500 mt-1">{result.model}</p>
              </div>

              <div className="p-4">
                {result.loading && (
                  <div className="flex flex-col items-center justify-center py-12 gap-3">
                    <Loader2 className="w-8 h-8 text-violet-500 animate-spin" />
                    <p className="text-sm text-zinc-500">Generating review...</p>
                  </div>
                )}

                {result.error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                    {result.error}
                  </div>
                )}

                {result.review && (
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown
                      components={{
                        h2: ({ children }) => (
                          <h2 className="text-base font-semibold text-zinc-200 mb-2 mt-4">{children}</h2>
                        ),
                        h3: ({ children }) => (
                          <h3 className="text-sm font-medium text-zinc-300 mb-2 mt-3">{children}</h3>
                        ),
                        p: ({ children }) => (
                          <p className="text-zinc-400 mb-2 text-xs leading-relaxed">{children}</p>
                        ),
                        ul: ({ children }) => (
                          <ul className="list-disc list-inside space-y-1 text-zinc-400 mb-3 text-xs">{children}</ul>
                        ),
                        code: ({ children, className }) => {
                          const isBlock = className?.includes('language-');
                          if (isBlock) {
                            return (
                              <pre className="bg-zinc-950 border border-zinc-800 rounded p-3 overflow-x-auto my-3">
                                <code className="text-xs text-zinc-300 font-mono">{children}</code>
                              </pre>
                            );
                          }
                          return (
                            <code className="bg-zinc-800 px-1 py-0.5 rounded text-xs text-violet-400 font-mono">
                              {children}
                            </code>
                          );
                        },
                      }}
                    >
                      {result.review.review}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ComparisonMode;
