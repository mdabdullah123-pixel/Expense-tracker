"""
AI Financial Assistant page - Chat interface for financial questions.

Users can ask questions about their finances and get AI-powered responses
based on their actual expense and income data. Supports questions about:
- Spending patterns
- Savings advice
- Budget suggestions
- Spending predictions
- Unusual spending patterns
"""

import streamlit as st
import logging
from datetime import date, datetime

from services.analytics_service import AnalyticsService
from utils.helpers import format_currency

logger = logging.getLogger(__name__)


# List of example questions for the AI assistant
EXAMPLE_QUESTIONS = [
    "Where am I spending the most money?",
    "How can I save more money this month?",
    "Summarize my monthly expenses",
    "Suggest a budget for me",
    "Detect any unusual spending patterns",
    "What's my financial health score?",
    "How much did I spend on food this month?",
    "Predict my spending for next month",
]


def render_ai_assistant():
    """Render the AI Financial Assistant chat page."""
    st.title("🤖 AI Financial Assistant")
    st.markdown("Your personal AI-powered financial advisor")
    st.divider()

    # Check if AI is configured
    ai_service = st.session_state.get("ai_service")
    if not ai_service or not ai_service.is_configured:
        st.warning(
            "⚠️ **AI service not configured.** "
            "Please go to the **Settings** page to configure an AI provider."
        )
        st.info(
            "Once configured, you'll be able to ask questions about your "
            "finances and get personalized insights."
        )

        # Show example of what's possible
        with st.expander("💡 What can I ask?"):
            for q in EXAMPLE_QUESTIONS:
                st.markdown(f"- *{q}*")
        return

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display current AI provider info
    st.caption(
        f"Using **{ai_service.provider}** - Model: **{ai_service.model}**"
    )

    # Quick action buttons
    st.subheader("⚡ Quick Questions")
    quick_cols = st.columns(2)
    quick_questions = [
        "Where am I spending the most?",
        "How can I save money?",
        "Summarize my expenses",
        "Detect unusual spending",
    ]

    for i, question in enumerate(quick_questions):
        col = quick_cols[i % 2]
        if col.button(question, width="stretch", key=f"quick_{i}"):
            # Add question to chat and process
            st.session_state.chat_history.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
            _process_question(question, ai_service)

    st.divider()

    # Chat interface
    st.subheader("💬 Chat with your Financial Assistant")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp", "")

            if role == "user":
                st.markdown(
                    f"<div style='text-align: right; background-color: #1E3A5F; "
                    f"padding: 10px; border-radius: 10px; margin: 5px 0;'>"
                    f"<b>You</b> ({timestamp}): {content}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='background-color: #2D2D44; padding: 10px; "
                    f"border-radius: 10px; margin: 5px 0;'>"
                    f"<b>🤖 Assistant</b> ({timestamp}):<br>{content}</div>",
                    unsafe_allow_html=True,
                )

    # Input area
    st.divider()

    # Custom question input
    with st.form("chat_input_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_question = st.text_input(
                "Ask a question about your finances",
                placeholder="e.g., Where am I spending the most?",
                label_visibility="collapsed",
                key="user_question_input",
            )
        with col2:
            submitted = st.form_submit_button("Send 📤", width="stretch")

        if submitted and user_question:
            # Add to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
            _process_question(user_question, ai_service)
            st.rerun()

    # Example questions dropdown
    with st.expander("💡 Need ideas? Try these questions"):
        for q in EXAMPLE_QUESTIONS:
            if st.button(q, key=f"example_{q}", width="stretch"):
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": q,
                    "timestamp": datetime.now().strftime("%H:%M"),
                })
                _process_question(q, ai_service)
                st.rerun()

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", width="stretch", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()


def _process_question(question: str, ai_service):
    """
    Process a user's financial question and get AI response.
    
    Args:
        question: The user's question
        ai_service: Configured AI service instance
    """
    with st.spinner("🧠 AI is analyzing your financial data..."):
        try:
            # Get spending data context
            data_context = AnalyticsService.build_ai_context()

            # Get unusual spending alerts for additional context
            unusual = AnalyticsService.detect_unusual_spending()
            if unusual:
                data_context += "\n\n=== UNUSUAL SPENDING PATTERNS ===\n"
                for item in unusual:
                    data_context += (
                        f"{item['category']}: {item['type']} by "
                        f"{abs(item['deviation']):.1f}% "
                        f"(Current: ₹{item['current']:.2f}, "
                        f"Avg: ₹{item['average']:.2f})\n"
                    )

            # Get current month summary for fresh context
            monthly = AnalyticsService.get_current_month_summary()
            data_context += "\n\n=== CURRENT MONTH SNAPSHOT ===\n"
            data_context += f"Month: {date.today().strftime('%B %Y')}\n"
            data_context += f"Expenses: ₹{monthly['total_expense']:.2f}\n"
            data_context += f"Income: ₹{monthly['total_income']:.2f}\n"
            data_context += f"Savings: ₹{monthly['savings']:.2f}\n"
            data_context += f"Top Category: {monthly['top_category']}\n"

            # Get AI response
            response = ai_service.ask_financial_question(question, data_context)

            if response:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                })
            else:
                # Fallback response with actual data
                fallback = _generate_fallback_response(question)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": fallback,
                    "timestamp": datetime.now().strftime("%H:%M"),
                })

        except Exception as e:
            logger.error("AI assistant error: %s", str(e))
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"❌ I encountered an error processing your question. "
                           f"Please try again or check your AI provider settings.\n\n"
                           f"Error: {str(e)}",
                "timestamp": datetime.now().strftime("%H:%M"),
            })


def _generate_fallback_response(question: str) -> str:
    """
    Generate a fallback response using actual data when AI is unavailable.
    
    Args:
        question: The user's question
        
    Returns:
        Response text with actual financial data
    """
    monthly = AnalyticsService.get_current_month_summary()
    total_expenses = AnalyticsService.get_total_expenses()
    total_income = AnalyticsService.get_total_income()
    category_data = AnalyticsService.get_category_breakdown()

    # Build response based on question keywords
    question_lower = question.lower()
    response_parts = []

    response_parts.append("📊 **Here's what I found from your financial data:**\n")

    if "spend" in question_lower or "expense" in question_lower or "money" in question_lower:
        response_parts.append(f"**Total Expenses:** {format_currency(total_expenses)}")
        response_parts.append(f"**Current Month:** {format_currency(monthly['total_expense'])}")
        response_parts.append(f"**Top Category:** {monthly['top_category']}\n")

        if category_data:
            response_parts.append("**Category Breakdown:**")
            for cat, amt in sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
                response_parts.append(f"- {cat}: {format_currency(amt)} ({pct:.1f}%)")

    elif "save" in question_lower or "budget" in question_lower:
        savings = total_income - total_expenses
        savings_rate = (savings / total_income * 100) if total_income > 0 else 0

        response_parts.append(f"**Total Income:** {format_currency(total_income)}")
        response_parts.append(f"**Total Expenses:** {format_currency(total_expenses)}")
        response_parts.append(f"**Current Savings:** {format_currency(savings)}")
        response_parts.append(f"**Savings Rate:** {savings_rate:.1f}%\n")

        if savings_rate < 20:
            response_parts.append("💡 **Tip:** Aim to save at least 20% of your income.")
            if category_data:
                top_cat = max(category_data, key=category_data.get)
                response_parts.append(
                    f"📌 Your biggest expense category is **{top_cat}** "
                    f"({format_currency(category_data[top_cat])}). "
                    f"Consider reducing this to save more."
                )

    elif "summary" in question_lower or "overview" in question_lower:
        response_parts.append(f"**Period:** Current Month ({date.today().strftime('%B %Y')})")
        response_parts.append(f"**Income:** {format_currency(monthly['total_income'])}")
        response_parts.append(f"**Expenses:** {format_currency(monthly['total_expense'])}")
        response_parts.append(f"**Savings:** {format_currency(monthly['savings'])}")
        response_parts.append(f"**Transactions:** {monthly['expense_count']} expenses, "
                              f"{monthly['income_count']} income entries")
        response_parts.append(f"**Top Category:** {monthly['top_category']}")

    else:
        response_parts.append(f"**Total Income:** {format_currency(total_income)}")
        response_parts.append(f"**Total Expenses:** {format_currency(total_expenses)}")
        response_parts.append(f"**Savings:** {format_currency(total_income - total_expenses)}")
        response_parts.append(f"**Monthly Transactions:** {monthly['expense_count']}")

    return "\n".join(response_parts)