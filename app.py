"""
AI-Powered Expense Tracker - Main Application Entry Point.

A modern personal finance application built with Streamlit that helps users
track expenses, manage income, and gain financial insights using AI.

Features:
    - Expense and Income tracking with CRUD operations
    - Interactive Plotly dashboard with financial metrics
    - AI-powered expense categorization
    - AI Financial Assistant for personalized advice
    - AI-generated spending reports (weekly/monthly)
    - Receipt scanning with OCR
    - Multiple AI providers (Ollama, OpenAI, Gemini, OpenRouter)
    - Dark-mode friendly UI
    
Usage:
    streamlit run app.py
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Ensure the project root is in the Python path
sys.path.insert(0, str(Path(__file__).parent))

import logging
from database.db import init_db
from database.repository import SettingsRepository
from services.ai_service import AIService
from utils.helpers import setup_logging

# Configure logging
setup_logging()

logger = logging.getLogger(__name__)


# --- Page Configuration ---
st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Initialize Session State ---
def init_session_state():
    """Initialize all session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
        st.session_state.ai_service = AIService()
        st.session_state.ai_provider = None
        st.session_state.ai_model = None
        st.session_state.chat_history = []
        st.session_state.ollama_url = "http://localhost:11434"
        st.session_state.ollama_model = "llama3"
        st.session_state.cloud_provider = "openai"
        st.session_state.openai_key = ""
        st.session_state.openai_model = "gpt-3.5-turbo"
        st.session_state.gemini_key = ""
        st.session_state.gemini_model = "gemini-1.5-flash"
        st.session_state.openrouter_key = ""
        st.session_state.openrouter_model = "anthropic/claude-3-haiku"
        st.session_state.openrouter_url = "https://openrouter.ai/api/v1"

        # Try to load saved settings from database
        try:
            saved = SettingsRepository.get_settings()
            if saved:
                st.session_state.ai_provider = saved.provider
                st.session_state.ai_model = saved.model
        except Exception as e:
            logger.warning("Could not load saved settings: %s", str(e))

        st.session_state.initialized = True


# --- Custom CSS for dark theme styling ---
def apply_custom_css():
    """Apply custom CSS for dark theme and improved UI."""
    st.markdown(
        """
        <style>
        /* Main background and text */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Metric cards styling */
        .stMetric {
            background-color: #1E1E2E;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Sidebar styling */
        .css-1d391kg, .css-12oz5g7 {
            background-color: #1A1A2E;
        }
        
        /* Chat message styling */
        .chat-user {
            background-color: #1E3A5F;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        
        .chat-assistant {
            background-color: #2D2D44;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        
        /* Divider styling */
        .stDivider {
            border-color: #333;
        }
        
        /* Info/Warning/Error boxes */
        .stAlert {
            border-radius: 8px;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
        
        /* Progress bar */
        .stProgress > div > div {
            background-color: #4ECDC4;
        }
        
        /* Dataframe */
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Success message animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stAlert {
            animation: fadeIn 0.3s ease-in-out;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1E1E2E;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #4ECDC4;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #45B7D1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- Sidebar Navigation ---
def render_sidebar():
    """Render the sidebar navigation."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="color: #4ECDC4; font-size: 2em;">💰</h1>
                <h2 style="color: #E0E0E0; margin: 0;">AI Expense Tracker</h2>
                <p style="color: #888; font-size: 0.8em;">v1.0.0</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Navigation
        st.markdown("### 📍 Navigation")

        page = st.radio(
            "Go to",
            options=[
                "🏠 Dashboard",
                "💳 Expenses",
                "📑 Reports",
                "🤖 AI Assistant",
                "⚙️ Settings",
            ],
            label_visibility="collapsed",
            key="nav_radio",
        )

        st.divider()

        # AI Provider Status
        st.markdown("### 🤖 AI Status")
        ai_service = st.session_state.get("ai_service")
        if ai_service and ai_service.is_configured:
            st.success(f"✅ **{ai_service.provider}** active")
            st.caption(f"Model: {ai_service.model}")
        else:
            st.warning("⚠️ Not configured")
            st.caption("Go to Settings to configure")

        st.divider()

        # Quick Summary
        st.markdown("### 📊 Quick Summary")
        from services.analytics_service import AnalyticsService
        from utils.helpers import format_currency

        total_expenses = AnalyticsService.get_total_expenses()
        total_income = AnalyticsService.get_total_income()
        savings = total_income - total_expenses

        st.markdown(f"**Income:** {format_currency(total_income)}")
        st.markdown(f"**Expenses:** {format_currency(total_expenses)}")
        st.markdown(f"**Savings:** {format_currency(savings)}")

        st.divider()

        # Footer
        st.markdown(
            """
            <div style="text-align: center; color: #666; font-size: 0.7em;">
                Built with ❤️ for Hackathons<br>
                Powered by AI
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Map radio selection to page functions
    page_map = {
        "🏠 Dashboard": "dashboard",
        "💳 Expenses": "expenses",
        "📑 Reports": "reports",
        "🤖 AI Assistant": "ai_assistant",
        "⚙️ Settings": "settings",
    }
    return page_map[page]


# --- Main Application ---
def main():
    """Main application entry point."""
    # Initialize
    init_session_state()
    apply_custom_css()

    # Initialize database
    try:
        init_db()
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        st.error(f"❌ Database initialization failed: {str(e)}")
        st.stop()

    # Render sidebar and get selected page
    selected_page = render_sidebar()

    # Render the selected page
    st.divider()

    if selected_page == "dashboard":
        from pages.dashboard import render_dashboard
        render_dashboard()

    elif selected_page == "expenses":
        from pages.expenses import render_expenses
        render_expenses()

    elif selected_page == "reports":
        from pages.reports import render_reports
        render_reports()

    elif selected_page == "ai_assistant":
        from pages.ai_assistant import render_ai_assistant
        render_ai_assistant()

    elif selected_page == "settings":
        from pages.settings import render_settings
        render_settings()


if __name__ == "__main__":
    main()