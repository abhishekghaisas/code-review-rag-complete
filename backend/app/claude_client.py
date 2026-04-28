"""
Direct Anthropic Claude Client for Code Review
Alternative to OpenRouter - uses Anthropic API directly
"""

import os
from typing import Optional
import anthropic
import logging

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Anthropic Claude API directly"""
    
    # Available Claude models
    MODELS = [
        {
            "id": "claude-haiku-4-5-20251001",
            "name": "Claude Haiku 4.5",
            "cost": "$1/1M input, $5/1M output",
            "quality": "9/10",
            "description": "Latest Haiku - Fast and cost-effective"
        },
        {
            "id": "claude-sonnet-4-20250514",
            "name": "Claude Sonnet 4",
            "cost": "$3/1M input, $15/1M output",
            "quality": "10/10",
            "description": "Latest and most capable Claude model"
        },
        {
            "id": "claude-3-5-sonnet-20241022",
            "name": "Claude 3.5 Sonnet",
            "cost": "$3/1M input, $15/1M output",
            "quality": "9.5/10",
            "description": "Excellent for code review"
        },
        {
            "id": "claude-3-5-haiku-20241022",
            "name": "Claude 3.5 Haiku",
            "cost": "$0.80/1M input, $4/1M output",
            "quality": "9/10",
            "description": "Previous generation Haiku"
        },
        {
            "id": "claude-3-haiku-20240307",
            "name": "Claude 3 Haiku",
            "cost": "$0.25/1M input, $1.25/1M output",
            "quality": "8.5/10",
            "description": "Cheapest option"
        }
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("Claude client initialized successfully")
    
    def review_code(
        self,
        code: str,
        context: str = "",
        language: str = "python",
        model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 2000,
        temperature: float = 0.3
    ) -> str:
        """
        Generate code review using Claude
        
        Args:
            code: Code snippet to review
            context: Similar code patterns from the codebase (RAG context)
            language: Programming language
            model: Claude model ID to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 - 1.0)
            
        Returns:
            Generated code review as string
        """
        
        # Build the review prompt
        prompt = self._build_review_prompt(code, context, language)
        
        try:
            logger.info(f"Generating review with model: {model}")
            
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system="You are a senior software engineer performing code review. Be specific, constructive, and actionable in your feedback.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            review = message.content[0].text
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
    
    def get_available_models(self):
        """Get list of available Claude models"""
        return {"models": self.MODELS}
    
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
        # Pricing per million tokens
        pricing = {
            "claude-haiku-4-5-20251001": {
                "input": 1.00 / 1_000_000,
                "output": 5.00 / 1_000_000
            },
            "claude-sonnet-4-20250514": {
                "input": 3.00 / 1_000_000,
                "output": 15.00 / 1_000_000
            },
            "claude-3-5-sonnet-20241022": {
                "input": 3.00 / 1_000_000,
                "output": 15.00 / 1_000_000
            },
            "claude-3-5-haiku-20241022": {
                "input": 0.80 / 1_000_000,
                "output": 4.00 / 1_000_000
            },
            "claude-3-haiku-20240307": {
                "input": 0.25 / 1_000_000,
                "output": 1.25 / 1_000_000
            }
        }
        
        if model in pricing:
            cost = (
                input_tokens * pricing[model]["input"] +
                output_tokens * pricing[model]["output"]
            )
            return round(cost, 6)
        
        # Default to Haiku 4.5 pricing
        return (
            input_tokens * 1.00 / 1_000_000 +
            output_tokens * 5.00 / 1_000_000
        )


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ClaudeClient()
    
    # Example code to review
    code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item
    return total
"""
    
    # Generate review
    review = client.review_code(
        code=code,
        language="python",
        model="claude-haiku-4-5-20251001"
    )
    
    print("=== Code Review ===")
    print(review)
