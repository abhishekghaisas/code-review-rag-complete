"""
Simplified RAG Engine for Code Review - No heavy ML dependencies
Uses keyword matching instead of semantic embeddings for Railway deployment
"""

from typing import List, Dict
import re
from app.claude_client import ClaudeClient

class CodeReviewRAG:
    def __init__(self):
        self.code_chunks: List[Dict[str, str]] = []
        self.claude_client = ClaudeClient()
    
    def ingest_code(self, code: str, filename: str = "code.py", language: str = "python"):
        """Store code chunks for retrieval"""
        # Simple chunking: split by functions/classes
        chunks = self._chunk_code(code, language)
        
        for i, chunk in enumerate(chunks):
            self.code_chunks.append({
                "id": f"{filename}_{i}",
                "code": chunk,
                "filename": filename,
                "language": language
            })
    
    def _chunk_code(self, code: str, language: str) -> List[str]:
        """Simple code chunking without tree-sitter"""
        lines = code.split('\n')
        chunks = []
        current_chunk = []
        
        for line in lines:
            # Start new chunk on function/class definitions
            if language == "python":
                if line.strip().startswith(('def ', 'class ', 'async def ')):
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                else:
                    current_chunk.append(line)
            elif language == "javascript":
                if re.match(r'^\s*(function|class|const\s+\w+\s*=\s*\()', line):
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                    current_chunk = [line]
                else:
                    current_chunk.append(line)
            else:
                current_chunk.append(line)
            
            # Create chunk every 50 lines
            if len(current_chunk) >= 50:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks if chunks else [code]
    
    def retrieve_relevant_code(self, code_to_review: str, top_k: int = 3) -> List[str]:
        """Simple keyword-based retrieval"""
        if not self.code_chunks:
            return []
        
        # Extract keywords from code to review
        keywords = self._extract_keywords(code_to_review)
        
        # Score chunks by keyword overlap
        scored_chunks = []
        for chunk in self.code_chunks:
            chunk_keywords = self._extract_keywords(chunk["code"])
            overlap = len(keywords & chunk_keywords)
            if overlap > 0:
                scored_chunks.append((overlap, chunk["code"]))
        
        # Return top K most relevant chunks
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in scored_chunks[:top_k]]
    
    def _extract_keywords(self, code: str) -> set:
        """Extract simple keywords from code"""
        # Remove comments and strings
        code = re.sub(r'["\'].*?["\']', '', code)
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # Extract identifiers (function names, variable names, etc.)
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
        
        # Filter out common keywords
        stopwords = {'def', 'class', 'import', 'from', 'if', 'else', 'for', 'while', 
                     'return', 'function', 'const', 'let', 'var', 'async', 'await'}
        return set(w.lower() for w in words if w.lower() not in stopwords)
    
    async def review_code(
        self,
        code: str,
        model: str = "claude-haiku-4-5-20251001",
        language: str = "python",
        use_rag: bool = False
    ) -> dict:
        """Generate code review using Claude API"""
        
        # Build context from RAG if enabled
        context = ""
        if use_rag and self.code_chunks:
            relevant_chunks = self.retrieve_relevant_code(code, top_k=3)
            if relevant_chunks:
                context = "\n\n".join([
                    f"### Related Code Pattern {i+1}:\n```{language}\n{chunk}\n```"
                    for i, chunk in enumerate(relevant_chunks)
                ])
        
        # Construct the review prompt
        prompt = f"""You are an expert code reviewer. Analyze the following {language} code and provide:

1. **Overall Assessment** (1-2 sentences)
2. **Issues Found** (if any):
   - Security vulnerabilities
   - Performance problems
   - Code smells
   - Bugs
3. **Suggestions for Improvement**
4. **Positive Aspects** (what's done well)

{"### Codebase Context:" + chr(10) + context + chr(10) if context else ""}

### Code to Review:
```{language}
{code}
```

Provide a thorough, constructive review."""

        try:
            # Call Claude API
            review_text = await self.claude_client.generate_review(prompt, model)
            
            return {
                "review": review_text,
                "model": model,
                "language": language,
                "rag_enabled": use_rag,
                "context_used": bool(context),
                "chunks_retrieved": len(relevant_chunks) if use_rag else 0
            }
        
        except Exception as e:
            raise Exception(f"Review generation failed: {str(e)}")
    
    def clear_codebase(self):
        """Clear all stored code chunks"""
        self.code_chunks = []
    
    def get_stats(self) -> dict:
        """Get codebase statistics"""
        return {
            "total_chunks": len(self.code_chunks),
            "files": len(set(chunk["filename"] for chunk in self.code_chunks)),
            "languages": list(set(chunk["language"] for chunk in self.code_chunks))
        }