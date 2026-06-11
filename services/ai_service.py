"""
AI Service Factory - Central entry point for all AI operations.

Provides a unified interface for expense categorization, financial analysis,
receipt parsing, and report generation across all supported AI providers.
Users can seamlessly switch between Local AI (Ollama) and Cloud AI providers.
"""

import logging
from typing import Optional, Tuple

from services.ollama_service import OllamaService
from services.openai_service import OpenAIService
from services.gemini_service import GeminiService
from services.openrouter_service import OpenRouterService

logger = logging.getLogger(__name__)


class AIService:
    """
    Factory class that creates and manages AI service instances.
    
    Provides unified methods for all AI operations while allowing
    users to switch between providers transparently.
    
    Supported providers:
        - ollama: Local inference via Ollama
        - openai: Cloud AI via OpenAI API
        - gemini: Cloud AI via Google Gemini API
        - openrouter: Cloud AI via OpenRouter
    """
    
    def __init__(self):
        """Initialize the AI service with no active provider."""
        self._provider = None
        self._service = None
        self._model = None
        self._api_key = None
        
    def configure(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Configure and initialize the AI service provider.
        
        Args:
            provider: AI provider name (ollama, openai, gemini, openrouter)
            model: Model name for the provider
            api_key: API key (required for cloud providers)
            base_url: Custom base URL (for ollama and openrouter)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        self._provider = provider.lower()
        self._model = model
        
        try:
            if self._provider == "ollama":
                url = base_url or "http://localhost:11434"
                self._service = OllamaService(base_url=url, model=model)
                if self._service.validate_connection():
                    self._api_key = None
                    return True, "Connected to Ollama successfully"
                else:
                    self._service = None
                    return False, "Cannot connect to Ollama. Is it running?"
                    
            elif self._provider == "openai":
                if not api_key:
                    return False, "OpenAI API key is required"
                self._service = OpenAIService(api_key=api_key, model=model)
                self._api_key = api_key
                if self._service.validate_api_key():
                    return True, "OpenAI API key validated successfully"
                else:
                    self._service = None
                    return False, "Invalid OpenAI API key"
                    
            elif self._provider == "gemini":
                if not api_key:
                    return False, "Gemini API key is required"
                self._service = GeminiService(api_key=api_key, model=model)
                self._api_key = api_key
                if self._service.validate_api_key():
                    return True, "Gemini API key validated successfully"
                else:
                    self._service = None
                    return False, "Invalid Gemini API key"
                    
            elif self._provider == "openrouter":
                if not api_key:
                    return False, "OpenRouter API key is required"
                url = base_url or "https://openrouter.ai/api/v1"
                self._service = OpenRouterService(api_key=api_key, model=model, base_url=url)
                self._api_key = api_key
                if self._service.validate_api_key():
                    return True, "OpenRouter API key validated successfully"
                else:
                    self._service = None
                    return False, "Invalid OpenRouter API key"
            else:
                return False, f"Unknown provider: {provider}"
                
        except Exception as e:
            self._service = None
            logger.error("Failed to configure AI service: %s", str(e))
            return False, f"Configuration failed: {str(e)}"
    
    @property
    def is_configured(self) -> bool:
        """Check if the AI service is configured and ready."""
        return self._service is not None
    
    @property
    def provider(self) -> Optional[str]:
        """Get the current provider name."""
        return self._provider
    
    @property
    def model(self) -> Optional[str]:
        """Get the current model name."""
        return self._model
    
    def categorize_expense(self, description: str) -> Optional[str]:
        """
        Automatically suggest a category for an expense description.
        
        Args:
            description: Text description of the expense
            
        Returns:
            Category name or None if categorization fails
        """
        if not self._service:
            logger.warning("AI service not configured")
            return None
        return self._service.categorize_expense(description)
    
    def ask_financial_question(self, question: str, context: str) -> Optional[str]:
        """
        Ask a financial question with user expense data as context.
        
        Args:
            question: User's question about their finances
            context: User's expense data as formatted text
            
        Returns:
            AI response text or None on failure
        """
        if not self._service:
            logger.warning("AI service not configured")
            return None
        return self._service.ask_financial_question(question, context)
    
    def generate_report(self, report_type: str, data_context: str) -> Optional[str]:
        """
        Generate a spending report.
        
        Args:
            report_type: "weekly" or "monthly"
            data_context: Formatted expense data
            
        Returns:
            Report text in markdown format or None on failure
        """
        if not self._service:
            logger.warning("AI service not configured")
            return None
        return self._service.generate_report(report_type, data_context)
    
    def parse_receipt_text(self, receipt_text: str) -> Optional[dict]:
        """
        Parse receipt/extracted text to extract structured information.
        
        Args:
            receipt_text: Raw text extracted from receipt image
            
        Returns:
            Dictionary with merchant, date, amount, items or None on failure
        """
        if not self._service:
            logger.warning("AI service not configured")
            return None
        return self._service.parse_receipt_text(receipt_text)