import { Download, FileText, FileCode } from 'lucide-react';
import type { ReviewResponse } from '../api';

interface ExportReviewProps {
  code: string;
  language: string;
  review: ReviewResponse | null;
}

function ExportReview({ code, language, review }: ExportReviewProps) {
  if (!review) {
    return null;
  }

  const exportAsMarkdown = () => {
    const timestamp = new Date().toLocaleString();
    
    let markdown = `# Code Review Report\n\n`;
    markdown += `**Generated:** ${timestamp}\n`;
    markdown += `**Model:** ${review.model_used}\n`;
    markdown += `**Language:** ${language}\n`;
    markdown += `**RAG Enabled:** ${review.rag_enabled ? 'Yes' : 'No'}\n\n`;
    
    markdown += `---\n\n`;
    markdown += `## Code Under Review\n\n`;
    markdown += `\`\`\`${language}\n${code}\n\`\`\`\n\n`;
    
    markdown += `---\n\n`;
    markdown += `## Review\n\n`;
    markdown += review.review;
    
    if (review.similar_code && review.similar_code.length > 0) {
      markdown += `\n\n---\n\n`;
      markdown += `## Similar Code Found\n\n`;
      review.similar_code.forEach((simCode, index) => {
        const meta = review.similar_code_metadata[index];
        markdown += `### ${index + 1}. ${meta?.file_path || 'Unknown file'}\n\n`;
        if (meta?.function_name) {
          markdown += `**Function:** ${meta.function_name}\n\n`;
        }
        markdown += `\`\`\`${meta?.language || language}\n${simCode}\n\`\`\`\n\n`;
      });
    }
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code-review-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportAsText = () => {
    const timestamp = new Date().toLocaleString();
    
    let text = `CODE REVIEW REPORT\n`;
    text += `${'='.repeat(80)}\n\n`;
    text += `Generated: ${timestamp}\n`;
    text += `Model: ${review.model_used}\n`;
    text += `Language: ${language}\n`;
    text += `RAG Enabled: ${review.rag_enabled ? 'Yes' : 'No'}\n\n`;
    
    text += `${'='.repeat(80)}\n\n`;
    text += `CODE UNDER REVIEW:\n\n`;
    text += code;
    text += `\n\n${'='.repeat(80)}\n\n`;
    
    text += `REVIEW:\n\n`;
    text += review.review;
    
    if (review.similar_code && review.similar_code.length > 0) {
      text += `\n\n${'='.repeat(80)}\n\n`;
      text += `SIMILAR CODE FOUND:\n\n`;
      review.similar_code.forEach((simCode, index) => {
        const meta = review.similar_code_metadata[index];
        text += `${index + 1}. ${meta?.file_path || 'Unknown file'}\n`;
        if (meta?.function_name) {
          text += `   Function: ${meta.function_name}\n`;
        }
        text += `\n${simCode}\n\n`;
      });
    }
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code-review-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportAsJSON = () => {
    const exportData = {
      timestamp: new Date().toISOString(),
      code,
      language,
      review: review,
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code-review-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = async () => {
    const text = review.review;
    try {
      await navigator.clipboard.writeText(text);
      alert('Review copied to clipboard!');
    } catch (err) {
      alert('Failed to copy to clipboard');
    }
  };

  return (
    <div className="bg-zinc-900 rounded-xl border border-zinc-800 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export Review
        </h3>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={exportAsMarkdown}
          className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2"
        >
          <FileText className="w-4 h-4" />
          Markdown
        </button>

        <button
          onClick={exportAsText}
          className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2"
        >
          <FileCode className="w-4 h-4" />
          Text
        </button>

        <button
          onClick={exportAsJSON}
          className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2"
        >
          <FileText className="w-4 h-4" />
          JSON
        </button>

        <button
          onClick={copyToClipboard}
          className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2"
        >
          <FileText className="w-4 h-4" />
          Copy
        </button>
      </div>

      <div className="mt-3 text-xs text-zinc-500">
        Export includes code, review, and similar code examples
      </div>
    </div>
  );
}

export default ExportReview;
