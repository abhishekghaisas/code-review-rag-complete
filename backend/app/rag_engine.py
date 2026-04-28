"""
RAG Engine for Code Review
Combines vector database retrieval with LLM generation for context-aware code reviews.
"""

import os
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging

from .claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class CodeReviewRAG:
    """
    RAG Engine for code review
    
    Workflow:
    1. Embed code using local sentence-transformers
    2. Retrieve similar code from ChromaDB
    3. Build context from retrieved code
    4. Generate review using OpenRouter LLM
    """
    
    def __init__(
        self,
        db_path: str = "./data/chroma_db",
        collection_name: str = "code_chunks",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize RAG engine
        
        Args:
            db_path: Path to ChromaDB storage
            collection_name: Name of the collection
            embedding_model: Sentence transformer model name
        """
        logger.info("Initializing Code Review RAG engine...")
        
        # Initialize local embeddings (FREE!)
        self.embedding_model_name = embedding_model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        logger.info(f"Embedding model loaded. Dimension: {self.embedder.get_sentence_embedding_dimension()}")
        
        # Initialize ChromaDB (FREE!)
        logger.info(f"Initializing ChromaDB at: {db_path}")
        self.chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection_name = collection_name
        try:
            self.collection = self.chroma_client.get_collection(
                name=collection_name
            )
            logger.info(f"Loaded existing collection: {collection_name}")
            logger.info(f"Collection size: {self.collection.count()} documents")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Initialize Claude client
        self.llm = ClaudeClient()
        self.llm_provider = "claude"
        logger.info("Using Anthropic Claude for LLM")
        logger.info("RAG engine initialization complete!")
    
    def ingest_code(
        self,
        code_chunks: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Ingest code chunks into vector database
        
        Args:
            code_chunks: List of dictionaries with structure:
                [{
                    "id": "unique_id",
                    "code": "code content",
                    "language": "python",
                    "metadata": {
                        "file_path": "path/to/file.py",
                        "function_name": "function_name",
                        "repo": "repo_name",
                        ...
                    }
                }, ...]
                
        Returns:
            Dictionary with ingestion statistics
        """
        if not code_chunks:
            logger.warning("No code chunks provided for ingestion")
            return {"status": "error", "message": "No code chunks provided"}
        
        logger.info(f"Starting ingestion of {len(code_chunks)} code chunks...")
        
        # Extract components
        ids = [chunk["id"] for chunk in code_chunks]
        codes = [chunk["code"] for chunk in code_chunks]
        metadatas = [chunk.get("metadata", {}) for chunk in code_chunks]
        
        # Add language to metadata if not present
        for i, chunk in enumerate(code_chunks):
            if "language" not in metadatas[i]:
                metadatas[i]["language"] = chunk.get("language", "unknown")
        
        # Generate embeddings locally (FREE!)
        logger.info("Generating embeddings...")
        embeddings = self.embedder.encode(
            codes,
            show_progress_bar=True,
            batch_size=32
        ).tolist()
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Store in ChromaDB
        logger.info("Storing in vector database...")
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=codes,
                metadatas=metadatas
            )
            logger.info(f"✅ Successfully ingested {len(code_chunks)} code chunks")
            
            return {
                "status": "success",
                "chunks_ingested": len(code_chunks),
                "collection_size": self.collection.count()
            }
        except Exception as e:
            logger.error(f"Error during ingestion: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def retrieve_similar_code(
        self,
        query_code: str,
        n_results: int = 3,
        language_filter: Optional[str] = None
    ) -> Tuple[List[str], List[Dict]]:
        """
        Retrieve similar code from vector database
        
        Args:
            query_code: Code to find similar examples for
            n_results: Number of results to return
            language_filter: Optional language filter
            
        Returns:
            Tuple of (similar_codes, metadatas)
        """
        logger.info(f"Retrieving {n_results} similar code chunks...")
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query_code]).tolist()
        
        # Build filter if language specified
        where_filter = None
        if language_filter:
            where_filter = {"language": language_filter}
        
        # Query ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where_filter
            )
            
            similar_codes = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            logger.info(f"Retrieved {len(similar_codes)} similar code chunks")
            return similar_codes, metadatas
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return [], []
    
    def review_code(
        self,
        code: str,
        language: str = "python",
        model: str = "meta-llama/llama-3.2-3b-instruct:free",
        use_rag: bool = True,
        n_similar: int = 3
    ) -> Dict[str, any]:
        """
        End-to-end code review with RAG
        
        Args:
            code: Code snippet to review
            language: Programming language
            model: OpenRouter model to use
            use_rag: Whether to use RAG retrieval
            n_similar: Number of similar code examples to retrieve
            
        Returns:
            Dictionary with review, similar code, and metadata
        """
        logger.info(f"Starting code review (RAG: {use_rag}, Model: {model})...")
        
        # Step 1: Retrieve similar code if RAG is enabled
        similar_codes = []
        metadatas = []
        context = ""
        
        if use_rag and self.collection.count() > 0:
            similar_codes, metadatas = self.retrieve_similar_code(
                query_code=code,
                n_results=n_similar,
                language_filter=language
            )
            
            # Build context from similar code
            if similar_codes:
                context_parts = []
                for i, (similar_code, metadata) in enumerate(zip(similar_codes, metadatas)):
                    file_path = metadata.get('file_path', 'unknown')
                    func_name = metadata.get('function_name', '')
                    
                    context_parts.append(
                        f"Example {i+1} ({file_path}"
                        f"{' - ' + func_name if func_name else ''}):\n"
                        f"```{language}\n{similar_code}\n```"
                    )
                
                context = "\n\n".join(context_parts)
                logger.info(f"Built context from {len(similar_codes)} similar examples")
        else:
            if self.collection.count() == 0:
                logger.info("No code in vector database yet - review without RAG context")
            else:
                logger.info("RAG disabled - review without context")
        
        # Step 2: Generate review using OpenRouter
        try:
            review = self.llm.review_code(
                code=code,
                context=context,
                language=language,
                model=model
            )
            
            return {
                "review": review,
                "similar_code": similar_codes,
                "similar_code_metadata": metadatas,
                "model_used": model,
                "rag_enabled": use_rag,
                "context_used": bool(context)
            }
            
        except Exception as e:
            logger.error(f"Error generating review: {str(e)}")
            return {
                "error": str(e),
                "review": None,
                "similar_code": similar_codes,
                "similar_code_metadata": metadatas,
                "model_used": model,
                "rag_enabled": use_rag
            }
    
    def get_stats(self) -> Dict[str, any]:
        """Get statistics about the vector database"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "embedding_model": self.embedding_model_name,
                "embedding_dimension": self.embedder.get_sentence_embedding_dimension()
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}
    
    def reset_database(self):
        """Reset the vector database (use with caution!)"""
        logger.warning("Resetting vector database...")
        self.chroma_client.delete_collection(name=self.collection_name)
        self.collection = self.chroma_client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Database reset complete")


# Example usage
if __name__ == "__main__":
    # Initialize RAG engine
    rag = CodeReviewRAG()
    
    # Example: Ingest some code
    sample_chunks = [
        {
            "id": "example_1",
            "code": "def calculate_sum(numbers):\n    return sum(numbers)",
            "language": "python",
            "metadata": {
                "file_path": "utils/math.py",
                "function_name": "calculate_sum"
            }
        },
        {
            "id": "example_2",
            "code": "def get_total(items):\n    total = 0\n    for item in items:\n        total += item\n    return total",
            "language": "python",
            "metadata": {
                "file_path": "helpers/array.py",
                "function_name": "get_total"
            }
        }
    ]
    
    # Ingest
    result = rag.ingest_code(sample_chunks)
    print(f"Ingestion result: {result}")
    
    # Review code
    code_to_review = """
def sum_list(lst):
    result = 0
    for i in range(len(lst)):
        result = result + lst[i]
    return result
"""
    
    review_result = rag.review_code(
        code=code_to_review,
        language="python",
        model="meta-llama/llama-3.2-3b-instruct:free"
    )
    
    print("\n=== Code Review ===")
    print(review_result['review'])
    print(f"\nUsed {len(review_result['similar_code'])} similar examples")
