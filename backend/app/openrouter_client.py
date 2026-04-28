"""
OpenRouter Client for Code Review
Provides interface to OpenRouter API with support for free and paid models.
"""

import os
from typing import Optional, Dict, List
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    # Available models configuration
    FREE_MODELS = [
        {
            "id": "meta-llama/llama-3.2-3b-instruct:free",
            "name": "Llama 3.2 3B",
            "cost": "$0.00",
            "quality": "7/10",
            "description": "Fast, free model good for development"
        },
        {
            "id": "google/gemini-flash-1.5:free",
            "name": "Gemini Flash 1.5",
            "cost": "$0.00",
            "quality": "7.5/10",
            "description": "Google's fast free model"
        },
        {
            "id": "mistralai/mistral-7b-instruct:free",
            "name": "Mistral 7B",
            "cost": "$0.00",
            "quality": "7/10",
            "description": "Open-source instruction-tuned model"
        }
    ]
    
    PAID_MODELS = [
        {
            "id": "anthropic/claude-3.5-haiku",
            "name": "Claude 3.5 Haiku",
            "cost": "$0.002/review",
            "quality": "9/10",
            "description": "Best quality, fast responses"
        },
        {
            "id": "openai/gpt-4o-mini",
            "name": "GPT-4o Mini",
            "cost": "$0.001/review",
            "quality": "8.5/10",
            "description": "Good balance of cost and quality"
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        logger.info("OpenRouter client initialized successfully")
    
    def review_code(
        self,
        code: str,
        context: str = "",
        language: str = "python",
        model: str = "meta-llama/llama-3.2-3b-instruct:free",
        max_tokens: int = 800,
        temperature: float = 0.3
    ) -> str:
        """
        Generate code review using OpenRouter
        
        Args:
            code: Code snippet to review
            context: Similar code patterns from the codebase (RAG context)
            language: Programming language
            model: Model ID to use (default: free Llama 3.2)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 - 1.0)
            
        Returns:
            Generated code review as string
        """
        
        # Build the review prompt
        prompt = self._build_review_prompt(code, context, language)
        
        try:
            logger.info(f"Generating review with model: {model}")
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer performing code review. "
                                   "Be specific, constructive, and actionable in your feedback."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            review = response.choices[0].message.content
            logger.info("Review generated successfully")
            return review
            
        except Exception as e:
            logger.error(f"Error generating review: {str(e)}")
            raise Exception(f"Failed to generate review: {str(e)}")
    
    def _build_review_prompt(
        self,
        code: str,
        context: str,
        language: str
    ) -> str:
        """Build the prompt for code review"""
        
        prompt = f"""You are an expert code reviewer. Review the following {language} code and provide specific, actionable feedback.

CODE TO REVIEW:
```{language}
{code}
```
"""
        
        if context:
            prompt += f"""
SIMILAR CODE PATTERNS FROM THIS CODEBASE:
{context}
"""
        
        prompt += """
Provide a concise review with:
🐛 **Bugs or Issues**: Potential bugs, edge cases, or errors
⚡ **Performance**: Performance concerns or optimizations
✨ **Style & Best Practices**: Code style, naming, structure
💡 **Suggestions**: Concrete improvements with examples

Be specific and reference line numbers or code snippets when possible.
Keep the review concise but actionable."""
        
        return prompt
    
    def get_available_models(self) -> Dict[str, List[Dict]]:
        """
        Get list of available models
        
        Returns:
            Dictionary with 'free' and 'paid' model lists
        """
        return {
            "free_models": self.FREE_MODELS,
            "paid_models": self.PAID_MODELS
        }
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """
        Estimate cost for a review
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model ID
            
        Returns:
            Estimated cost in USD
        """
        # Free models
        if any(m["id"] == model for m in self.FREE_MODELS):
            return 0.0
        
        # Paid models (approximate pricing)
        pricing = {
            "anthropic/claude-3.5-haiku": {
                "input": 0.25 / 1_000_000,
                "output": 1.25 / 1_000_000
            },
            "openai/gpt-4o-mini": {
                "input": 0.15 / 1_000_000,
                "output": 0.60 / 1_000_000
            }
        }
        
        if model in pricing:
            cost = (
                input_tokens * pricing[model]["input"] +
                output_tokens * pricing[model]["output"]
            )
            return round(cost, 6)
        
        return 0.0


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = OpenRouterClient()
    
    # Example code to review
    code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total
"""
    
    # Generate review with free model
    review = client.review_code(
        code=code,
        language="python",
        model="meta-llama/llama-3.2-3b-instruct:free"
    )
    
    print("=== Code Review ===")
    print(review)
    print("\n=== Available Models ===")
    models = client.get_available_models()
    print(f"Free models: {len(models['free_models'])}")
    print(f"Paid models: {len(models['paid_models'])}")
