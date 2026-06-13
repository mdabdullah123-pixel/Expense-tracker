"""
AI Financial Assistant page - Chat interface for financial questions.

Users can ask questions about their finances and get AI-powered responses
based on their actual expense and income data. Supports questions about:
- Spending patterns
- Savings advice
- Budget suggestions
- Spending predictions
- Unusual spending patterns

Works with or without an AI provider configured.
When no AI provider is set, uses data-driven fallback responses.
"""

import streamlit as st
import logging
from datetime import date, datetime

from services.analytics_service import AnalyticsService
from utils.helpers import format_currency
from database.repository import ExpenseRepository

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
    "Which category has the highest spending?",
    "Compare this month to last month",
]


def render_ai_assistant():
    """Render the AI Financial Assistant chat page."""
    st.title("🤖 AI Financial Assistant")
    st.markdown("Your personal AI-powered financial advisor")
    st.divider()

    # Check if AI is configured
    ai_service = st.session_state.get("ai_service")
    ai_available = ai_service and ai_service.is_configured

    # Initialize chat history in session state if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show AI provider status
    if ai_available:
        st.caption(
            f"Using **{ai_service.provider}** - Model: **{ai_service.model}**"
        )
    else:
        st.info(
            "💡 **AI mode:** Using your financial data for answers. "
            "Configure an AI provider in **Settings** for smarter AI-powered responses."
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
            _process_question(question, ai_service if ai_available else None)
            st.rerun()

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
            _process_question(user_question, ai_service if ai_available else None)
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
                _process_question(q, ai_service if ai_available else None)
                st.rerun()

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", width="stretch", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()


def _process_question(question: str, ai_service):
    """
    Process a user's financial question and get response.
    
    Uses AI if available, otherwise falls back to data-driven responses.
    
    Args:
        question: The user's question
        ai_service: Configured AI service instance or None
    """
    with st.spinner("🧠 Analyzing your financial data..."):
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

            # Try AI if available
            response = None
            if ai_service:
                response = ai_service.ask_financial_question(question, data_context)

            # Fallback response with actual data
            if not response:
                response = _generate_fallback_response(question)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M"),
            })

        except Exception as e:
            logger.error("AI assistant error: %s", str(e))
            # Even on error, show a helpful response
            fallback = _generate_fallback_response(question)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": fallback,
                "timestamp": datetime.now().strftime("%H:%M"),
            })


def _generate_fallback_response(question: str) -> str:
    """
    Generate a response using actual financial data.
    Provides intelligent answers even without AI.
    
    Args:
        question: The user's question
        
    Returns:
        Response text with actual financial data and insights
    """
    monthly = AnalyticsService.get_current_month_summary()
    total_expenses = AnalyticsService.get_total_expenses()
    total_income = AnalyticsService.get_total_income()
    category_data = AnalyticsService.get_category_breakdown()
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    # Get all expenses for trend analysis
    expense_df = AnalyticsService.get_expenses_dataframe()
    
    question_lower = question.lower()
    response_parts = []

    # Add a friendly greeting based on context
    response_parts.append("📊 **Here's what I found from your financial data:**\n")

    # Handle "spending" questions
    if any(word in question_lower for word in ["spend", "expense", "money", "most", "where", "category"]):
        response_parts.append(f"**Total All-Time Expenses:** {format_currency(total_expenses)}")
        response_parts.append(f"**Current Month:** {format_currency(monthly['total_expense'])}")
        response_parts.append(f"**Top Category:** {monthly['top_category']}\n")

        if category_data:
            response_parts.append("**📊 Spending by Category (Top 5):**")
            for i, (cat, amt) in enumerate(
                sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:5], 1
            ):
                pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                response_parts.append(f"{i}. **{cat}**: {format_currency(amt)} ({pct:.1f}%)")
            
            # Find where they spend the most
            top_cat = max(category_data, key=category_data.get)
            response_parts.append(f"\n💡 **Insight:** You spend the most on **{top_cat}** "
                                  f"({format_currency(category_data[top_cat])}).")

    # Handle "save" / "budget" questions
    elif any(word in question_lower for word in ["save", "budget", "reduce", "cut"]):
        response_parts.append(f"**Total Income:** {format_currency(total_income)}")
        response_parts.append(f"**Total Expenses:** {format_currency(total_expenses)}")
        response_parts.append(f"**Current Savings:** {format_currency(savings)}")
        response_parts.append(f"**Savings Rate:** {savings_rate:.1f}%\n")

        if savings_rate < 20:
            response_parts.append("💡 **Tip:** Aim to save at least 20% of your income.")
            if category_data:
                top_cat = max(category_data, key=category_data.get)
                top_amt = category_data[top_cat]
                response_parts.append(
                    f"📌 Your biggest expense category is **{top_cat}** "
                    f"({format_currency(top_amt)}). "
                    f"Reducing this by just 10% would save "
                    f"**{format_currency(top_amt * 0.1)}**!"
                )
        else:
            response_parts.append("✅ **Great job!** Your savings rate looks healthy.")

        # Budget suggestion
        if total_income > 0:
            response_parts.append("\n**📋 Suggested Monthly Budget:**")
            response_parts.append(f"- Needs (50%): {format_currency(total_income * 0.5)}")
            response_parts.append(f"- Wants (30%): {format_currency(total_income * 0.3)}")
            response_parts.append(f"- Savings (20%): {format_currency(total_income * 0.2)}")

    # Handle "summary" / "overview" questions
    elif any(word in question_lower for word in ["summary", "overview", "report", "month"]):
        response_parts.append(f"**Period:** Current Month ({date.today().strftime('%B %Y')})")
        response_parts.append(f"**Income:** {format_currency(monthly['total_income'])}")
        response_parts.append(f"**Expenses:** {format_currency(monthly['total_expense'])}")
        response_parts.append(f"**Savings:** {format_currency(monthly['savings'])}")
        response_parts.append(f"**Transactions:** {monthly['expense_count']} expenses, "
                              f"{monthly['income_count']} income entries")
        response_parts.append(f"**Top Category:** {monthly['top_category']}")
        
        # Trend if we have data
        if not expense_df.empty and len(expense_df) > 1:
            response_parts.append(
                f"\n📈 **Total History:** {format_currency(total_expenses)} across "
                f"all {len(expense_df)} transactions."
            )

    # Handle "unusual" / "pattern" / "detect" questions
    elif any(word in question_lower for word in ["unusual", "pattern", "detect", "abnormal", "anomaly"]):
        unusual = AnalyticsService.detect_unusual_spending()
        if unusual:
            response_parts.append("🚨 **Unusual Spending Patterns Detected:**\n")
            for item in unusual:
                if item["type"] == "overspend":
                    response_parts.append(
                        f"⚠️ **{item['category']}**: {item['deviation']:.0f}% **higher** than usual! "
                        f"(Current: {format_currency(item['current'])} vs "
                        f"Avg: {format_currency(item['average'])})"
                    )
                else:
                    response_parts.append(
                        f"✅ **{item['category']}**: {abs(item['deviation']):.0f}% **lower** than usual! "
                        f"(Current: {format_currency(item['current'])} vs "
                        f"Avg: {format_currency(item['average'])})"
                    )
        else:
            response_parts.append("✅ **No unusual patterns detected.** Your spending looks consistent.")
            response_parts.append(
                "\n💡 Add more transactions to get better spending pattern analysis."
            )

    # Handle "predict" / "future" questions
    elif any(word in question_lower for word in ["predict", "future", "forecast", "next month"]):
        if not expense_df.empty:
            monthly_avg = total_expenses / max(len(expense_df["month"].unique()), 1)
            response_parts.append(f"📊 **Based on your history:**")
            response_parts.append(f"- Average monthly spending: {format_currency(monthly_avg)}")
            response_parts.append(f"- Current month: {format_currency(monthly['total_expense'])}")
            
            if monthly['total_expense'] > monthly_avg:
                response_parts.append(f"\n⚠️ You're spending **{((monthly['total_expense']/monthly_avg)-1)*100:.0f}% more** "
                                      f"than average this month.")
            else:
                response_parts.append(f"\n✅ You're spending **{((1-monthly['total_expense']/monthly_avg))*100:.0f}% less** "
                                      f"than average this month. Keep it up!")
        else:
            response_parts.append("📊 Add some expenses first to get spending predictions.")

    # Handle "health" / "score" questions
    elif any(word in question_lower for word in ["health", "score", "rating", "good"]):
        # Calculate a simple financial health score
        expense_ratio = (total_expenses / total_income * 100) if total_income > 0 else 100
        categories_used = len(category_data)
        
        score = 100
        if expense_ratio > 80:
            score -= 30
        elif expense_ratio > 60:
            score -= 15
        elif expense_ratio > 40:
            score -= 5
        
        if categories_used <= 2:
            score -= 10
        if monthly['expense_count'] == 0:
            score -= 20
            
        score = max(0, min(100, score))
        
        response_parts.append(f"**🏆 Financial Health Score: {score}/100**\n")
        
        if score >= 80:
            response_parts.append("🌟 **Excellent!** Your finances are in great shape!")
        elif score >= 60:
            response_parts.append("👍 **Good!** Some room for improvement.")
        elif score >= 40:
            response_parts.append("⚠️ **Fair.** Consider reviewing your spending habits.")
        else:
            response_parts.append("🚨 **Needs attention.** Time to create a budget plan!")
        
        response_parts.append(f"\n**Breakdown:**")
        response_parts.append(f"- Expense-to-Income Ratio: {expense_ratio:.1f}%")
        response_parts.append(f"- Active Categories: {categories_used}")
        response_parts.append(f"- Monthly Transactions: {monthly['expense_count']}")

    # Handle "food" / specific category questions
    elif any(word in question_lower for word in ["food", "transport", "shopping", "entertainment", "health",
                                                   "education", "bills", "investment"]):
        # Find which category they're asking about
        target_cat = None
        for cat in ["Food", "Transport", "Shopping", "Entertainment", "Health", 
                    "Education", "Bills", "Investment"]:
            if cat.lower() in question_lower:
                target_cat = cat
                break
        
        if target_cat and target_cat in category_data:
            cat_total = category_data[target_cat]
            cat_pct = (cat_total / total_expenses * 100) if total_expenses > 0 else 0
            
            # Get recent expenses in this category
            cat_expenses = [e for e in ExpenseRepository.get_all_expenses() 
                          if e.category == target_cat][:5]
            
            response_parts.append(f"**📊 {target_cat} Spending Analysis:**")
            response_parts.append(f"- **Total spent on {target_cat}:** {format_currency(cat_total)}")
            response_parts.append(f"- **Percentage of total:** {cat_pct:.1f}%")
            
            if cat_expenses:
                response_parts.append(f"\n**Recent {target_cat} transactions:**")
                for e in cat_expenses[:5]:
                    response_parts.append(f"  • {e.date}: {e.description} - {format_currency(e.amount)}")
        else:
            response_parts.append(f"I couldn't find spending data for that category.")
            response_parts.append(f"**Your categories:** {', '.join(category_data.keys())}")

    # Default response for other questions
    else:
        response_parts.append(f"**Total Income:** {format_currency(total_income)}")
        response_parts.append(f"**Total Expenses:** {format_currency(total_expenses)}")
        response_parts.append(f"**Savings:** {format_currency(savings)}")
        response_parts.append(f"**Savings Rate:** {savings_rate:.1f}%")
        response_parts.append(f"**Monthly Transactions:** {monthly['expense_count']}")
        response_parts.append(f"\n💡 Try asking:\n"
                              f"- \"Where am I spending the most?\"\n"
                              f"- \"How can I save money?\"\n"
                              f"- \"What's my financial health score?\"")

    return "\n".join(response_parts)

