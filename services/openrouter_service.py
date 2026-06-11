"""
OpenRouter AI Service.

Provides integration with OpenRouter's unified API for accessing multiple AI models.
Supports Bring Your Own Key (BYOK) model - API keys are never hardcoded.
Lets users choose from various models like Claude, Gemini, Llama, etc. via OpenRouter.
"""

import json
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

OPENROUTER_DEFAULT_URL = "https://openrouter.ai/api/v1"


class OpenRouterService:
    """
    Service for interacting with OpenRouter's unified AI API.
    
    Provides access to multiple AI models through a single API,
    including Claude, Gemini, Llama, and more.
    """
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3-haiku", base_url: str = OPENROUTER_DEFAULT_URL):
        """
        Initialize the OpenRouter service.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier (e.g., "anthropic/claude-3-haiku", "google/gemini-pro")
            base_url: OpenRouter API base URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/chat/completions"
        
    def _make_request(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """
        Send a chat completion request to OpenRouter.
        
        Args:
            system_prompt: System-level instruction
            user_prompt: User's question/prompt
            
        Returns:
            Response text or None on failure
        """
        if not self.api_key:
            logger.error("OpenRouter API key not provided")
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://expense-tracker.app",
                "X-Title": "AI Expense Tracker",
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500,
            }
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            logger.error("OpenRouter request failed: %s", str(e))
            return None

    def categorize_expense(self, description: str) -> Optional[str]:
        """
        Automatically suggest a category for an expense description.
        
        Args:
            description: Text description of the expense
            
        Returns:
            Category name or None if categorization fails
        """
        system_prompt = """You are an expense categorization AI. 
Your task is to categorize expense descriptions into exactly one of these categories:
Food, Transport, Shopping, Entertainment, Health, Education, Bills, Investment, Salary, Other

Respond with ONLY the category name, nothing else."""
        
        user_prompt = f"Categorize this expense: {description}"
        response = self._make_request(system_prompt, user_prompt)
        
        if not response:
            return None
            
        response = response.strip().strip('"').strip("'")
        
        valid_categories = [
            "Food", "Transport", "Shopping", "Entertainment",
            "Health", "Education", "Bills", "Investment",
            "Salary", "Other"
        ]
        
        for category in valid_categories:
            if category.lower() in response.lower():
                return category
        
        return "Other"

    def ask_financial_question(self, question: str, context: str) -> Optional[str]:
        """
        Ask a financial question with user expense data as context.
        
        Args:
            question: User's question about their finances
            context: User's expense data as formatted text
            
        Returns:
            AI response text or None on failure
        """
        system_prompt = """You are a knowledgeable financial AI assistant. 
You help users understand their spending patterns and provide financial advice.
Use the provided expense data context to give personalized, actionable insights.
Be concise, practical, and encouraging."""
        
        user_prompt = f"""Context - User's financial data:
{context}

User's question: {question}

Provide a helpful, data-driven response:"""
        
        return self._make_request(system_prompt, user_prompt)

    def generate_report(self, report_type: str, data_context: str) -> Optional[str]:
        """
        Generate a spending report.
        
        Args:
            report_type: "weekly" or "monthly"
            data_context: Formatted expense data
            
        Returns:
            Report text in markdown format or None on failure
        """
        system_prompt = f"""You are a financial report generator. 
Generate a {report_type} spending report in markdown format.
Include key insights, spending patterns, and actionable recommendations.
Format with proper markdown headers, bullet points, and emphasis."""
        
        user_prompt = f"""Generate a {report_type} spending report based on this data:

{data_context}

Provide a comprehensive markdown report covering:
1. Total spending overview
2. Category breakdown
3. Key insights and trends
4. Savings suggestions
5. Financial health score (out of 100)"""
        
        return self._make_request(system_prompt, user_prompt)

    def parse_receipt_text(self, receipt_text: str) -> Optional[dict]:
        """
        Parse receipt/extracted text to extract structured information.
        
        Args:
            receipt_text: Raw text extracted from receipt image
            
        Returns:
            Dictionary with merchant, date, amount, items or None on failure
        """
        system_prompt = """You are a receipt parsing AI. 
Extract structured information from receipt text.
Respond ONLY with a valid JSON object containing:
{
    "merchant": "Store name or null",
    "date": "Date in YYYY-MM-DD format or null",
    "total": "Total amount as number or null",
    "items": ["Item 1", "Item 2", ...],
    "category_suggestion": "Suggested expense category"
}

If you cannot extract certain fields, use null. Do not add any text outside the JSON."""
        
        user_prompt = f"Parse this receipt:\n{receipt_text}"
        
        response = self._make_request(system_prompt, user_prompt)
        if not response:
            return None
            
        try:
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse receipt JSON from OpenRouter response")
            return None

    def validate_api_key(self) -> bool:
        """
        Validate the OpenRouter API key.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{self.base_url}/models", headers=headers)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning("OpenRouter API key validation failed: %s", str(e))
            return False