"""
Unit tests for AI service operations.

Tests the AI service factory, provider configuration,
and fallback behavior for expense categorization and responses.
"""

import pytest
from services.ai_service import AIService


class TestAIService:
    """Test the AI service factory and fallback behavior."""

    def test_ai_service_initialization(self):
        """Test AI service initializes in unconfigured state."""
        service = AIService()
        assert service.is_configured is False
        assert service.provider is None
        assert service.model is None

    def test_ai_service_categorize_unconfigured(self):
        """Test categorization returns None when not configured."""
        service = AIService()
        result = service.categorize_expense("Swiggy Order ₹450")
        assert result is None

    def test_ai_service_ask_unconfigured(self):
        """Test financial question returns None when not configured."""
        service = AIService()
        result = service.ask_financial_question("Where am I spending?", "context")
        assert result is None

    def test_ai_service_generate_report_unconfigured(self):
        """Test report generation returns None when not configured."""
        service = AIService()
        result = service.generate_report("monthly", "data")
        assert result is None

    def test_ai_service_parse_receipt_unconfigured(self):
        """Test receipt parsing returns None when not configured."""
        service = AIService()
        result = service.parse_receipt_text("receipt text")
        assert result is None

    def test_ai_service_configure_invalid_provider(self):
        """Test configuring with invalid provider returns error."""
        service = AIService()
        success, message = service.configure(
            provider="invalid_provider",
            model="test-model",
        )
        assert success is False
        assert "Unknown provider" in message
        assert service.is_configured is False


class TestAIProviderValidation:
    """Test AI provider validation logic."""

    def test_ollama_config_requires_no_key(self):
        """Test Ollama configuration doesn't require API key."""
        service = AIService()
        # This will fail because Ollama is not running in tests,
        # but it should fail on connection, not on missing API key
        success, message = service.configure(
            provider="ollama",
            model="llama3",
            base_url="http://localhost:11434",
        )
        assert success is False
        assert "Cannot connect" in message or "Connection" in message

    def test_openai_config_requires_key(self):
        """Test OpenAI configuration requires API key."""
        service = AIService()
        success, message = service.configure(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="",
        )
        assert success is False
        assert "API key is required" in message

    def test_gemini_config_requires_key(self):
        """Test Gemini configuration requires API key."""
        service = AIService()
        success, message = service.configure(
            provider="gemini",
            model="gemini-1.5-flash",
            api_key="",
        )
        assert success is False
        assert "API key is required" in message

    def test_openrouter_config_requires_key(self):
        """Test OpenRouter configuration requires API key."""
        service = AIService()
        success, message = service.configure(
            provider="openrouter",
            model="anthropic/claude-3-haiku",
            api_key="",
        )
        assert success is False
        assert "API key is required" in message