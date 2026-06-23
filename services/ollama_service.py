"""
Ollama AI Service for local model inference.

Provides integration with locally running Ollama models (llama3, mistral, gemma3).
Supports expense categorization, financial advice, receipt parsing, and report generation.
Uses HTTP requests to communicate with the Ollama API at configurable endpoint.
"""

import json
import logging

import httpx

logger = logging.getLogger(__name__)

OLLAMA_DEFAULT_URL = "http://localhost:11434"


class OllamaService:
    """
    Service for interacting with locally deployed Ollama models.

    Provides AI-powered expense categorization, financial analysis,
    and receipt parsing using local LLM inference.
    """

    def __init__(self, base_url: str = OLLAMA_DEFAULT_URL, model: str = "llama3"):
        """
        Initialize the Ollama service.

        Args:
            base_url: Ollama API endpoint URL
            model: Model name to use (llama3, mistral, gemma3)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_url = f"{self.base_url}/api/generate"

    def _make_request(
        self, prompt: str, system_prompt: str | None = None
    ) -> str | None:
        """
        Send a prompt to the Ollama model and get a response.

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system instruction

        Returns:
            Response text or None on failure
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }

            if system_prompt:
                payload["system"] = system_prompt

            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "").strip()

        except httpx.ConnectError:
            logger.warning("Cannot connect to Ollama at %s", self.base_url)
            return None
        except httpx.TimeoutException:
            logger.warning("Ollama request timed out")
            return None
        except Exception as e:
            logger.error("Ollama request failed: %s", str(e))
            return None

    def categorize_expense(self, description: str) -> str | None:
        """
        Automatically suggest a category for an expense description.

        Args:
            description: Text description of the expense

        Returns:
            Category name or None if categorization fails

        Examples:
            "Swiggy Order ₹450" -> "Food"
            "Uber Ride ₹250" -> "Transport"
            "Movie Ticket ₹300" -> "Entertainment"
        """
        system_prompt = """You are an expense categorization AI.
Your task is to categorize expense descriptions into exactly one of these categories:
Food, Transport, Shopping, Entertainment, Health, Education, Bills, Investment, Salary, Other

Respond with ONLY the category name, nothing else. No explanation, no punctuation."""

        prompt = f"Categorize this expense: {description}"

        response = self._make_request(prompt, system_prompt)
        if not response:
            return None

        # Clean and validate the response
        response = response.strip().strip('"').strip("'")

        valid_categories = [
            "Food",
            "Transport",
            "Shopping",
            "Entertainment",
            "Health",
            "Education",
            "Bills",
            "Investment",
            "Salary",
            "Other",
        ]

        # Find the best matching category
        for category in valid_categories:
            if category.lower() in response.lower():
                return category

        # If no match, return "Other" as fallback
        return "Other"

    def ask_financial_question(self, question: str, context: str) -> str | None:
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

        prompt = f"""Context - User's financial data:
{context}

User's question: {question}

Provide a helpful, data-driven response:"""

        return self._make_request(prompt, system_prompt)

    def generate_report(self, report_type: str, data_context: str) -> str | None:
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

        prompt = f"""Generate a {report_type} spending report based on this data:

{data_context}

Provide a comprehensive markdown report covering:
1. Total spending overview
2. Category breakdown
3. Key insights and trends
4. Savings suggestions
5. Financial health score (out of 100)"""

        return self._make_request(prompt, system_prompt)

    def parse_receipt_text(self, receipt_text: str) -> dict | None:
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

        prompt = f"Parse this receipt:\n{receipt_text}"

        response = self._make_request(prompt, system_prompt)
        if not response:
            return None

        try:
            # Try to extract JSON from the response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])

            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse receipt JSON from Ollama response")
            return None

    def validate_connection(self) -> bool:
        """
        Check if Ollama is accessible and the model is available.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])

                # Check if our model is in the list
                model_names = [m.get("name", "") for m in models]
                logger.info("Available Ollama models: %s", model_names)
                return True

        except Exception as e:
            logger.warning("Ollama connection validation failed: %s", str(e))
            return False
