# AI Agents & Tools — AI-Powered Expense Tracker

This document describes the AI agents, services, and tools integrated into the Expense Tracker application. It is intended for developers, AI enthusiasts, and anyone interested in understanding how AI powers this application.

## Overview

The Expense Tracker uses a **multi-provider AI architecture** that supports both local and cloud-based AI models. A unified `AIService` factory pattern abstracts provider-specific implementations, making it easy to switch between or add new AI backends.

---

## Architecture

```
User Request
    │
    ▼
pages/ (UI Layer)
    │
    ▼
services/ai_service.py (AI Service Factory)
    │
    ├── services/ollama_service.py    → Local LLM (Ollama)
    ├── services/openai_service.py    → OpenAI API
    ├── services/gemini_service.py    → Google Gemini API
    └── services/openrouter_service.py → OpenRouter API
```

### AI Service Factory

The `AIService` class in `services/ai_service.py` acts as a **facade** that:

- Selects the appropriate provider based on user configuration
- Validates provider availability and credentials
- Handles fallbacks gracefully when a provider is unavailable
- Formats prompts consistently across providers
- Parses responses into structured output

### Supported AI Providers

| Provider | Type | Models | Cost |
|----------|------|--------|------|
| **Ollama** | Local | llama3, mistral, gemma3 | Free (offline) |
| **OpenAI** | Cloud (BYOK) | GPT-3.5-turbo, GPT-4 | API key required |
| **Google Gemini** | Cloud (BYOK) | Gemini 1.5 Flash, Pro | API key required |
| **OpenRouter** | Cloud (BYOK) | Claude, Gemini, Llama, Mistral, etc. | API key required |

---

## AI Agent Capabilities

### 1. Expense Categorization Agent

**File:** `services/ai_service.py` — `suggest_category()` method

- **Input:** Expense description string
- **Output:** Suggested category from predefined list
- **Prompt:** Few-shot learning with category examples
- **Fallback:** Rule-based keyword matching if AI unavailable

**Example:**
```python
suggest_category("Uber ride to airport")
# Returns: "Transportation"
```

### 2. Financial Assistant Agent

**File:** `pages/ai_assistant.py`

- **Purpose:** Chat-based personal financial advisor
- **Input:** User's natural language question + transaction data context
- **Output:** Personalized financial insight or advice
- **Context Injection:** Appends recent expenses, income, and analytics to the prompt

**Capabilities:**
- Spending analysis ("Where am I spending the most?")
- Savings advice ("How can I save more money?")
- Budget suggestions ("Suggest a budget for me")
- Anomaly detection ("Detect unusual spending patterns")
- Spending prediction ("Predict my future spending")

**Prompt Engineering:**
- System prompt restricts the assistant to finance-related topics only
- Non-financial questions receive a polite redirect
- Uses few-shot examples to improve response quality

### 3. Spending Report Agent

**File:** `pages/reports.py`

- **Purpose:** Generate structured weekly/monthly spending reports
- **Input:** Transaction data filtered by date range
- **Output:** Formatted markdown report with sections:
  - Spending overview
  - Category breakdown
  - Savings suggestions
  - Budget recommendations (monthly)
  - Financial health score (monthly)

**Financial Health Score:**
- Calculated based on income-to-expense ratio, savings rate, and spending diversity
- Scale: 0–100

### 4. Receipt Scanner Agent

**File:** `utils/receipt_parser.py`

- **Purpose:** Extract structured data from receipt images
- **Pipeline:**
  1. **OCR (Tesseract):** Extract raw text from image
  2. **AI Parsing (optional):** Use LLM to structure extracted text
  3. **Regex Parsing (fallback):** Pattern match for merchant, date, total, items

**Extracted Fields:**
- Merchant name
- Date of purchase
- Total amount
- Line items with prices

**Fallback Chain:**
1. Tesseract OCR → AI-enhanced parsing → Apply to form
2. Tesseract OCR → Regex parsing → Apply to form
3. Error message with manual entry suggestion

---

## Provider-Specific Implementations

### Ollama Service (`services/ollama_service.py`)

```python
class OllamaService:
    endpoint: str  # e.g., http://localhost:11434
    model: str     # e.g., llama3, mistral, gemma3
```

- Communicates via REST API to local Ollama instance
- Supports streaming responses
- No API key required
- Works fully offline

### OpenAI Service (`services/openai_service.py`)

```python
class OpenAIService:
    api_key: str
    model: str  # gpt-3.5-turbo or gpt-4
```

- Uses the official OpenAI Python SDK
- Supports GPT-3.5-turbo and GPT-4 models
- Requires user-provided API key (BYOK)

### Gemini Service (`services/gemini_service.py`)

```python
class GeminiService:
    api_key: str
    model: str  # gemini-1.5-flash or gemini-1.5-pro
```

- Uses the Google Generative AI Python SDK
- Supports Gemini 1.5 Flash and Pro models
- Requires user-provided API key (BYOK)

### OpenRouter Service (`services/openrouter_service.py`)

```python
class OpenRouterService:
    api_key: str
    model: str  # e.g., anthropic/claude-3-haiku, google/gemini-pro
```

- Uses OpenRouter's unified API
- Access to 200+ models from various providers
- Requires user-provided API key (BYOK)

---

## Analytics Service

**File:** `services/analytics_service.py`

Not an AI agent per se, but provides data-driven fallbacks when AI is unavailable:

| Function | Description |
|----------|-------------|
| `get_total_income()` | Sum of all income records |
| `get_total_expenses()` | Sum of all expense records |
| `get_spending_by_category()` | Grouped spending per category |
| `get_top_categories()` | Highest spending categories |
| `get_monthly_trends()` | Income/expense over time |
| `detect_anomalies()` | Flags unusually large transactions |
| `get_financial_health_score()` | 0–100 score based on financial ratios |

---

## Security & Privacy

| Feature | Implementation |
|---------|---------------|
| **API Key Storage** | Stored only in Streamlit session state (browser session) |
| **Key Persistence** | NEVER written to database or disk |
| **Session Cleanup** | Keys cleared on browser close |
| **Data Privacy** | AI calls are server-side; only transaction data is sent |
| **Local AI Option** | Full offline mode with Ollama (no data leaves your machine) |

---

## Adding a New AI Provider

To add a new AI provider:

1. Create a new service file in `services/` (e.g., `services/anthropic_service.py`)
2. Implement the required interface:
   ```python
   class AnthropicService:
       def __init__(self, api_key: str, model: str = "claude-3-opus"):
           ...
       def chat(self, messages: list) -> str:
           ...
   ```
3. Register the provider in `services/ai_service.py`:
   ```python
   from services.anthropic_service import AnthropicService
   
   class AIService:
       PROVIDERS = {
           "ollama": OllamaService,
           "openai": OpenAIService,
           "gemini": GeminiService,
           "openrouter": OpenRouterService,
           "anthropic": AnthropicService,  # New provider
       }
   ```
4. Add the provider UI in `pages/settings.py`

---

## Dependencies

AI-related Python packages from `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `openai` | OpenAI API SDK |
| `google-generativeai` | Google Gemini SDK |
| `requests` | HTTP client (Ollama, OpenRouter) |
| `pytesseract` | OCR text extraction |
| `Pillow` | Image processing for receipts |

---

## Testing AI Services

```bash
# Run AI service tests
pytest tests/test_ai_service.py -v

# Run all tests with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

Tests mock external API calls to avoid requiring actual API keys during testing.

---

## References

- [Ollama Documentation](https://github.com/ollama/ollama)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)
- [OpenRouter API](https://openrouter.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io)