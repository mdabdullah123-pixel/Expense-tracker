# 💰 AI-Powered Expense Tracker

A modern, production-ready personal finance application built with **Streamlit** that helps users track expenses, manage income, and gain intelligent financial insights using AI.

> **Built for Hackathons** - Fully functional, demo-ready application with AI-powered features.

---

## ✨ Features

### 📊 Dashboard
- **Real-time financial overview** - Total Income, Expenses, Savings metrics
- **Interactive Plotly charts** - Category spending pie, monthly trends, income vs expense bars
- **Top spending categories** - Identify where your money goes
- **Spending alerts** - Detect unusual spending patterns automatically
- **Recent transactions** - Quick view of latest expenses

### 💳 Expense & Income Tracking (CRUD)
- **Add expenses** with date, amount, category, description, payment method
- **Add income** with date, amount, source
- **View all transactions** with search and filter
- **Delete** individual records
- **AI-powered category suggestions** from expense descriptions

### 🤖 AI Financial Assistant
- Chat interface to ask questions about your finances
- Personalized insights using **actual user expense data**
- Questions supported:
  - "Where am I spending the most?"
  - "How can I save more money?"
  - "Summarize my monthly expenses"
  - "Suggest a budget for me"
  - "Detect unusual spending patterns"
  - "Predict my future spending"
- **Intelligent fallback** when AI is unavailable - uses actual data

### 📑 AI Spending Reports
- **Weekly Reports** - Total spending, major categories, savings suggestions
- **Monthly Reports** - Spending trends, financial health score, budget recommendations
- **Download as Markdown** for sharing or documentation

### 📸 Receipt Scanner
- Upload receipt images (PNG, JPG, JPEG, WebP)
- **OCR text extraction** using Tesseract (with graceful fallback)
- Auto-extract: Merchant name, Date, Total amount, Line items
- **Auto-populate expense form** from scanned data
- **AI-enhanced parsing** for complex receipts

### ⚙️ AI Provider System
- **Local AI** - Ollama (llama3, mistral, gemma3)
- **Cloud AI (BYOK)**:
  - OpenAI (GPT-3.5, GPT-4)
  - Google Gemini (Flash, Pro)
  - OpenRouter (Claude, Gemini, Llama, Mistral)
- **Seamless switching** between providers
- **Secure key handling** - Keys stored only in session state, never persisted

---

## 🏗️ Architecture

```
expense-tracker/
│
├── app.py                      # Main entry point, sidebar navigation, session state
├── requirements.txt            # Python dependencies
├── .env.example                # Environment configuration template
├── sample_data.py              # Sample data generator (100+ expenses)
│
├── database/                   # Data layer
│   ├── db.py                   # Database connection, initialization
│   ├── models.py               # SQLAlchemy models (Expense, Income, Settings)
│   └── repository.py          # Repository pattern (CRUD operations)
│
├── pages/                      # Streamlit UI pages
│   ├── dashboard.py            # Financial overview with charts
│   ├── expenses.py             # Expense/Income CRUD + Receipt scanner
│   ├── reports.py              # AI-powered spending reports
│   ├── ai_assistant.py         # Chat-based financial advisor
│   └── settings.py             # AI provider configuration
│
├── services/                   # Business logic
│   ├── ai_service.py           # AI Service Factory (unified interface)
│   ├── ollama_service.py       # Ollama local inference
│   ├── openai_service.py       # OpenAI cloud API
│   ├── gemini_service.py       # Google Gemini API
│   ├── openrouter_service.py   # OpenRouter API
│   └── analytics_service.py    # Financial calculations & metrics
│
├── utils/                      # Utilities
│   ├── charts.py               # Plotly chart builder (dark theme)
│   ├── helpers.py              # Currency formatting, validation, logging
│   └── receipt_parser.py       # OCR receipt extraction & parsing
│
├── tests/                      # Test suite
│   ├── test_database.py        # Database CRUD tests
│   └── test_ai_service.py      # AI service tests
│
└── data/                       # Runtime data (created automatically)
    ├── expense_tracker.db      # SQLite database
    └── app.log                 # Application logs
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Python 3.14+ recommended)
- **pip** (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd expense-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Create .env file for API keys
cp .env.example .env
# Edit .env with your API keys
```

### Run the Application

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

### (Optional) Generate Sample Data

```bash
python sample_data.py
```

This creates 100 sample expenses and 12 months of income records for testing.

---

## 🤖 AI Provider Setup

### Option 1: Local AI (Ollama) - Free & Offline

1. **Install Ollama** from [ollama.ai](https://ollama.ai)
2. **Pull a model**:
   ```bash
   ollama pull llama3     # 4.7GB - Recommended
   ollama pull mistral    # 4.1GB - Faster
   ollama pull gemma3     # 4.0GB - Efficient
   ```
3. **Start Ollama** (usually runs as a service)
4. In the app, go to **Settings** → **Local AI (Ollama)** → **Test Connection**

### Option 2: Cloud AI (BYOK - Bring Your Own Key)

#### OpenAI
1. Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. In the app: **Settings** → **Cloud AI** → **OpenAI**
3. Enter your key and select model (GPT-3.5-turbo or GPT-4)

#### Google Gemini
1. Get an API key from [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. In the app: **Settings** → **Cloud AI** → **Gemini**
3. Enter your key and select model

#### OpenRouter
1. Get an API key from [openrouter.ai/keys](https://openrouter.ai/keys)
2. In the app: **Settings** → **Cloud AI** → **OpenRouter**
3. Enter your key and select model (Claude, Gemini, Llama, etc.)

### Security Note
- **API keys are NEVER stored in the database**
- Keys are kept only in **Streamlit session state** (browser session)
- Keys are cleared when you close the browser
- All API calls are made server-side; keys never reach the frontend

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_database.py -v
pytest tests/test_ai_service.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

---

## 🛡️ Security

- **SQL Injection Protection**: All database queries use parameterized SQLAlchemy ORM
- **Input Validation**: All user inputs are validated and sanitized
- **Secure API Key Handling**: Keys stored only in session state, never in database
- **Graceful Error Handling**: All exceptions are caught and logged; never expose internals
- **Logging**: Comprehensive logging to file and console for debugging

---

## 💻 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.14+** | Core programming language |
| **Streamlit** | Web application framework |
| **SQLite + SQLAlchemy** | Database and ORM |
| **Pandas** | Data processing and analytics |
| **Plotly** | Interactive charts and visualizations |
| **OpenAI SDK** | OpenAI API integration (BYOK) |
| **Google GenAI** | Gemini API integration (BYOK) |
| **Ollama** | Local LLM inference |
| **OpenRouter** | Unified AI API access |
| **Tesseract OCR** | Receipt text extraction |
| **Pillow** | Image processing |
| **pytest** | Unit testing |
| **python-dotenv** | Environment configuration |

---

## 📸 Screenshots

<!-- Screenshots placeholder - Add images here -->
| Dashboard | Expenses |
|:---:|:---:|
| *(Add screenshot)* | *(Add screenshot)* |

| AI Assistant | Reports |
|:---:|:---:|
| *(Add screenshot)* | *(Add screenshot)* |

---

## 📋 Project Requirements Checklist

### ✅ Mandatory Requirements
- [x] **AI-powered features** - Categorization, assistant, reports
- [x] **Local AI Inference** - Ollama support (llama3, mistral, gemma3)
- [x] **BYOK (Bring Your Own Key)** - OpenAI, Gemini, OpenRouter
- [x] **Choice between Local and Cloud AI** - Settings page toggle
- [x] **Fully functional and demo-ready** - Complete application

### ✅ Core Features
- [x] Expense CRUD with full field support
- [x] Income CRUD
- [x] Interactive Dashboard with Plotly charts
- [x] 10 expense categories
- [x] Multiple payment methods

### ✅ AI Features
- [x] AI Expense Categorization
- [x] AI Financial Assistant with chat
- [x] AI Spending Reports (weekly/monthly)
- [x] AI Receipt Scanner
- [x] AI Provider Management

### ✅ Technical Requirements
- [x] Repository pattern for database
- [x] SQLite database
- [x] Proper security (input validation, SQL injection protection)
- [x] Unit tests
- [x] Comprehensive documentation
- [x] Requirements.txt
- [x] Sample data generator

---

## 📝 License

This project is built for educational and hackathon purposes.

## 🙏 Acknowledgments

- Built with Streamlit - The fastest way to build data apps
- Powered by Ollama, OpenAI, Google Gemini, and OpenRouter
- OCR support via Tesseract