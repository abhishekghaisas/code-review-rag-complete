import { type ReviewResponse } from '../api';
import { Sparkles, FileCode } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ReviewPanelProps {
  review: ReviewResponse | null;
  loading: boolean;
}

function ReviewPanel({ review, loading }: ReviewPanelProps) {
  if (loading) {
    return (
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-8">
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <div className="w-12 h-12 border-4 border-violet-500/20 border-t-violet-500 rounded-full animate-spin" />
          <p className="text-zinc-400">Analyzing code with Claude...</p>
        </div>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-8">
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-zinc-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-zinc-300 mb-2">
              Ready to Review
            </h3>
            <p className="text-sm text-zinc-500">
              Paste your code and click "Review Code" to get AI-powered feedback
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
        <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide">
            AI Review
          </h2>
          <span className="text-xs text-zinc-500 font-mono">
            {review.model_used}
          </span>
        </div>
        <div className="p-6">
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              components={{
                h1: (props) => <h1 className="text-xl font-bold text-zinc-100 mb-4" {...props} />,
                h2: (props) => <h2 className="text-lg font-semibold text-zinc-200 mb-3 mt-6" {...props} />,
                h3: (props) => <h3 className="text-base font-medium text-zinc-300 mb-2 mt-4" {...props} />,
                p: (props) => <p className="text-zinc-400 mb-3 leading-relaxed" {...props} />,
                ul: (props) => <ul className="list-disc list-inside space-y-2 text-zinc-400 mb-4" {...props} />,
                ol: (props) => <ol className="list-decimal list-inside space-y-2 text-zinc-400 mb-4" {...props} />,
                code: (props) => {
                  const isBlock = props.className?.includes('language-');
                  if (isBlock) {
                    return (
                      <pre className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 overflow-x-auto my-4">
                        <code className="text-sm text-zinc-300 font-mono" {...props} />
                      </pre>
                    );
                  }
                  return <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-sm text-violet-400 font-mono" {...props} />;
                },
                strong: (props) => <strong className="text-zinc-200 font-semibold" {...props} />,
              }}
            >
              {review.review}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {review.similar_code && review.similar_code.length > 0 && (
        <div className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
          <div className="px-4 py-3 border-b border-zinc-800">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide flex items-center gap-2">
              <FileCode className="w-4 h-4" />
              Similar Code Found ({review.similar_code.length})
            </h2>
          </div>
          <div className="p-6 space-y-4">
            {review.similar_code.map((code, index) => (
              <div key={index} className="border border-zinc-800 rounded-lg overflow-hidden">
                <div className="px-3 py-2 bg-zinc-950 border-b border-zinc-800 text-xs text-zinc-500 font-mono">
                  {review.similar_code_metadata[index]?.file_path || 'Unknown file'}
                  {review.similar_code_metadata[index]?.function_name && (
                    <span className="text-violet-400">
                      {' → '}{review.similar_code_metadata[index].function_name}
                    </span>
                  )}
                </div>
                <pre className="p-4 overflow-x-auto">
                  <code className="text-sm text-zinc-300 font-mono">{code}</code>
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {review.rag_enabled && (
        <div className="flex items-center gap-2 text-xs text-zinc-500">
          <div className={`w-2 h-2 rounded-full ${review.context_used ? 'bg-green-500' : 'bg-yellow-500'}`} />
          <span>
            RAG {review.context_used ? 'enabled' : 'enabled but no similar code found'}
          </span>
        </div>
      )}
    </div>
  );
}

export default ReviewPanel;