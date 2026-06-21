# User Manual — AI-Powered Expense Tracker

A comprehensive guide to using the AI-Powered Expense Tracker application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Expenses & Income](#managing-expenses--income)
4. [AI Financial Assistant](#ai-financial-assistant)
5. [AI Spending Reports](#ai-spending-reports)
6. [Receipt Scanner](#receipt-scanner)
7. [Settings & AI Provider Configuration](#settings--ai-provider-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Launching the App

```bash
streamlit run app.py
```

The app opens in your browser at **http://localhost:8501**.

### Navigation

The sidebar contains the main navigation menu:

| Menu Item | Description |
|-----------|-------------|
| **Dashboard** | Financial overview with charts and metrics |
| **Expenses** | Add/view/delete expenses and income, scan receipts |
| **Reports** | Generate AI-powered spending reports |
| **AI Assistant** | Chat with an AI about your finances |
| **Settings** | Configure AI providers and preferences |

---

## Dashboard Overview

The Dashboard is your financial command center.

### Metrics Cards

At the top, you'll see four key metrics:

- **Total Income** — Sum of all income records (green)
- **Total Expenses** — Sum of all expense records (red)
- **Net Savings** — Income minus Expenses (blue)
- **Expense Count** — Total number of expense transactions

### Charts

| Chart | Description |
|-------|-------------|
| **Category Distribution (Pie)** | Shows spending breakdown by category |
| **Monthly Trends (Line)** | Income vs Expenses over time |
| **Income vs Expense (Bar)** | Side-by-side monthly comparison |

### Quick Features

- **Top Spending Categories** — Lists categories you spend the most on
- **Spending Alerts** — Automatically detects unusually large expenses
- **Recent Transactions** — Shows your 5 most recent entries

---

## Managing Expenses & Income

### Adding an Expense

1. Go to **Expenses** page
2. Expand **"➕ Add Expense"** section
3. Fill in the fields:
   - **Date** — Defaults to today
   - **Amount** — Enter the expense amount
   - **Category** — Select or type a custom category
   - **Description** — Briefly describe the expense
   - **Payment Method** — Cash, Card, UPI, etc.
4. Click **"Add Expense"**

> **AI Categorization Tip:** Type a description and the AI can suggest a category automatically.

### Adding Income

1. Go to **Expenses** page
2. Expand **"➕ Add Income"** section
3. Fill in:
   - **Date** — Defaults to today
   - **Amount** — Income amount
   - **Source** — e.g., Salary, Freelance, Investment
4. Click **"Add Income"**

### Viewing Transactions

- All transactions are displayed in a table below the add forms
- Use the **search bar** to filter by description
- Toggle between **All**, **Expenses**, or **Income** views
- Adjust the **date range** to filter by time period

### Deleting a Transaction

- Each transaction row has a **🗑 Delete** button
- Click it to permanently remove the record

---

## AI Financial Assistant

The AI Assistant is a chat interface that provides personalized financial advice based on **your actual expense data**.

### Starting a Chat

1. Go to **AI Assistant** page
2. Type your question in the chat input box
3. Press **Enter** to send

### Example Questions

| Question | What It Does |
|----------|-------------|
| "Where am I spending the most?" | Shows your top expense categories |
| "How can I save more money?" | Provides personalized saving tips |
| "Summarize my monthly expenses" | Gives a monthly spending summary |
| "Suggest a budget for me" | Creates a custom budget based on your spending |
| "Detect unusual spending patterns" | Flags abnormally large or frequent expenses |
| "Predict my future spending" | Estimates next month's spending trends |

### How It Works

- The AI analyzes your actual transaction data from the database
- Responses are tailored to your personal finances
- If no AI provider is configured, it falls back to data-driven insights

> **Note:** The assistant only answers finance-related questions based on your data. For general questions, it will politely redirect to financial topics.

---

## AI Spending Reports

Generate detailed reports about your spending habits.

### Generate a Report

1. Go to **Reports** page
2. Select the report type:
   - **Weekly Report** — Last 7 days
   - **Monthly Report** — Last 30 days
3. Click **"Generate Report"**

### What's Included

| Section | Description |
|---------|-------------|
| **Overview** | Total spent, transaction count, daily average |
| **Spending by Category** | Breakdown of spending per category |
| **Top Categories** | Your highest spending areas |
| **Savings Suggestions** | AI-generated tips to save money |
| **Budget Recommendation** | (Monthly) Suggested budget for next month |
| **Financial Health Score** | (Monthly) A score from 0-100 |

### Downloading Reports

- Reports include a **Download as Markdown** button
- Saves the report as a `.md` file for sharing or documentation

---

## Receipt Scanner

Scan receipts to auto-populate expense entries.

### How to Scan

1. Go to **Expenses** page
2. Expand **"📸 Scan Receipt"** section
3. Upload an image of a receipt (PNG, JPG, JPEG, WebP)
4. The app will extract:
   - **Merchant Name**
   - **Date**
   - **Total Amount**
   - **Line Items**
5. Click **"Apply to Expense Form"** to auto-fill a new expense

### Requirements

- Clear, well-lit receipt images work best
- Supported formats: PNG, JPG, JPEG, WebP
- Requires **Tesseract OCR** installed for optimal results
- Falls back gracefully if OCR is unavailable

---

## Settings & AI Provider Configuration

### Accessing Settings

Go to **Settings** page from the sidebar navigation.

### AI Provider Options

You can choose between **Local AI** (offline, free) and **Cloud AI** (requires API keys).

#### Option 1: Local AI (Ollama) — Free & Offline

1. Install [Ollama](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3
   ```
3. Start Ollama (runs as a background service)
4. In Settings:
   - Select **"Local AI (Ollama)"**
   - Enter the Ollama endpoint (default: `http://localhost:11434`)
   - Select a model (llama3, mistral, or gemma3)
   - Click **"Test Connection"** to verify

#### Option 2: Cloud AI (BYOK)

**OpenAI:**
1. Get an API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. In Settings → Select **OpenAI**
3. Enter your API key
4. Select model (GPT-3.5-turbo or GPT-4)
5. Click **"Save Settings"**

**Google Gemini:**
1. Get an API key from [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. In Settings → Select **Gemini**
3. Enter your API key
4. Select model (Flash or Pro)
5. Click **"Save Settings"**

**OpenRouter:**
1. Get an API key from [openrouter.ai](https://openrouter.ai/keys)
2. In Settings → Select **OpenRouter**
3. Enter your API key
4. Select a model (Claude, Gemini, Llama, Mistral, etc.)
5. Click **"Save Settings"**

### Security Notes

- **API keys are NEVER stored in the database**
- Keys are kept only in your browser session
- Keys are cleared when you close the browser
- All AI calls are made server-side

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **App won't start** | Ensure all dependencies are installed: `pip install -r requirements.txt` |
| **Blank charts** | Add some data first via the Expenses page or run `python sample_data.py` |
| **AI not responding** | Check that your AI provider is properly configured in Settings |
| **Ollama connection failed** | Ensure Ollama is running (`ollama serve`) and the endpoint URL is correct |
| **Receipt scan fails** | Verify Tesseract is installed, or try a clearer receipt image |
| **Database errors** | Delete `data/expense_tracker.db` and restart the app to reset |

### Getting Help

If you encounter issues not covered here:
- Check the application logs in `data/app.log`
- Review the README for additional setup instructions

---

© 2026 AI-Powered Expense Tracker
