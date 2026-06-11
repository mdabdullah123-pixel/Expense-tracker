"""
Google Gemini AI Service.

Provides integration with Google's Gemini API for expense categorization,
financial analysis, receipt parsing, and report generation.
Supports Bring Your Own Key (BYOK) model.
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Google's Gemini AI models.
    
    Provides AI-powered expense categorization, financial analysis,
    and receipt parsing using Gemini models via API key.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini service.
        
        Args:
            api_key: Google Gemini API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self._client = None
        self._init_client()
        
    def _init_client(self):
        """Initialize the Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai
            logger.info("Gemini client initialized with model: %s", self.model)
        except ImportError:
            logger.error("google.generativeai package not installed")
        except Exception as e:
            logger.error("Failed to initialize Gemini client: %s", str(e))
    
    def _make_request(self, prompt: str) -> Optional[str]:
        """
        Send a prompt to Gemini and get a response.
        
        Args:
            prompt: The text prompt
            
        Returns:
            Response text or None on failure
        """
        if not self._client:
            logger.error("Gemini client not initialized")
            return None
            
        try:
            model = self._client.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text.strip() if response.text else None
        except Exception as e:
            logger.error("Gemini request failed: %s", str(e))
            return None

    def categorize_expense(self, description: str) -> Optional[str]:
        """
        Automatically suggest a category for an expense description.
        
        Args:
            description: Text description of the expense
            
        Returns:
            Category name or None if categorization fails
        """
        prompt = f"""You are an expense categorization AI. 
Categorize this expense description into exactly one of these categories:
Food, Transport, Shopping, Entertainment, Health, Education, Bills, Investment, Salary, Other

Expense: {description}

Respond with ONLY the category name, nothing else."""
        
        response = self._make_request(prompt)
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
        prompt = f"""You are a knowledgeable financial AI assistant. 
You help users understand their spending patterns and provide financial advice.
Use the provided expense data context to give personalized, actionable insights.

Context - User's financial data:
{context}

User's question: {question}

Provide a helpful, data-driven response:"""
        
        return self._make_request(prompt)

    def generate_report(self, report_type: str, data_context: str) -> Optional[str]:
        """
        Generate a spending report.
        
        Args:
            report_type: "weekly" or "monthly"
            data_context: Formatted expense data
            
        Returns:
            Report text in markdown format or None on failure
        """
        prompt = f"""You are a financial report generator. 
Generate a {report_type} spending report in markdown format based on this data:

{data_context}

Provide a comprehensive markdown report covering:
1. Total spending overview
2. Category breakdown
3. Key insights and trends
4. Savings suggestions
5. Financial health score (out of 100)"""
        
        return self._make_request(prompt)

    def parse_receipt_text(self, receipt_text: str) -> Optional[dict]:
        """
        Parse receipt/extracted text to extract structured information.
        
        Args:
            receipt_text: Raw text extracted from receipt image
            
        Returns:
            Dictionary with merchant, date, amount, items or None on failure
        """
        prompt = f"""You are a receipt parsing AI. 
Extract structured information from the following receipt text.
Respond ONLY with a valid JSON object containing:
{{
    "merchant": "Store name or null if not found",
    "date": "Date in YYYY-MM-DD format or null",
    "total": "Total amount as number or null",
    "items": ["Item 1", "Item 2", ...],
    "category_suggestion": "Suggested expense category"
}}

Receipt text:
{receipt_text}

JSON response:"""
        
        response = self._make_request(prompt)
        if not response:
            return None
            
        try:
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse receipt JSON from Gemini response")
            return None

    def validate_api_key(self) -> bool:
        """
        Validate the Gemini API key.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            if not self._client:
                return False
            # List models as a lightweight validation
            models = self._client.list_models()
            return len(list(models)) > 0
        except Exception as e:
            logger.warning("Gemini API key validation failed: %s", str(e))
            return False