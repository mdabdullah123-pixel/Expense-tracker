"""
AI Financial Assistant - Simple Chatbot Interface.

A clean, simple chat interface where users can ask questions about their
finances and get clear, helpful answers based on their actual expense data.
Works without any AI provider configuration.
"""

import streamlit as st
import logging
from datetime import date, datetime
from services.analytics_service import AnalyticsService
from utils.helpers import format_currency
from database.repository import ExpenseRepository

logger = logging.getLogger(__name__)


def render_ai_assistant():
    """Render a simple AI Financial Assistant chatbot."""
    st.title("🤖 AI Assistant")
    st.markdown("Ask me anything about your finances!")

    # Initialize chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    ai_service = st.session_state.get("ai_service")
    use_ai = ai_service and ai_service.is_configured

    if use_ai:
        st.caption(f"Using **{ai_service.provider}** • Model: **{ai_service.model}**")
    else:
        st.caption("💡 Using your financial data for answers")

    # Chat display
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align:right;background:#1E3A5F;padding:10px;border-radius:10px;margin:5px 0'>"
                        f"<b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#2D2D44;padding:10px;border-radius:10px;margin:5px 0'>"
                        f"<b>🤖 Assistant:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

    # Quick questions
    with st.expander("⚡ Quick Questions", expanded=False):
        cols = st.columns(2)
        questions = [
            "Where am I spending the most?",
            "How can I save money?",
            "Show my monthly summary",
            "Check for unusual spending",
            "What's my financial health score?",
            "How much did I spend on food?",
            "Suggest a budget",
            "Predict next month's spending",
        ]
        for i, q in enumerate(questions):
            if cols[i % 2].button(q, key=f"qq_{i}", width="stretch"):
                answer = get_answer(q)
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        cols = st.columns([5, 1])
        with cols[0]:
            question = st.text_input("Ask a question", placeholder="e.g., Where am I spending the most?", label_visibility="collapsed")
        with cols[1]:
            submitted = st.form_submit_button("Send", width="stretch")

    if submitted and question:
        answer = get_answer(question)
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        st.button("🗑️ Clear Chat", on_click=lambda: st.session_state.chat_history.clear())


def get_answer(question: str) -> str:
    """Get a simple answer to a financial question."""
    q = question.lower()
    
    # Gather data once
    total_income = AnalyticsService.get_total_income()
    total_expenses = AnalyticsService.get_total_expenses()
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    category_data = AnalyticsService.get_category_breakdown()
    monthly = AnalyticsService.get_current_month_summary()
    
    # Spending questions
    if any(w in q for w in ["spend", "where", "most", "category", "expense"]):
        lines = [f"**Total Expenses:** {format_currency(total_expenses)}",
                 f"**This Month:** {format_currency(monthly['total_expense'])}",
                 f"**Top Category:** {monthly['top_category']}"]
        if category_data:
            lines.append("\n**By Category:**")
            for cat, amt in sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:5]:
                pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
                lines.append(f"• {cat}: {format_currency(amt)} ({pct:.0f}%)")
            top = max(category_data, key=category_data.get)
            lines.append(f"\n💡 You spend the most on **{top}** ({format_currency(category_data[top])})")
        return "\n".join(lines)
    
    # Savings questions
    if any(w in q for w in ["save", "budget", "reduce"]):
        lines = [f"**Income:** {format_currency(total_income)}",
                 f"**Expenses:** {format_currency(total_expenses)}",
                 f"**Savings:** {format_currency(savings)} ({savings_rate:.0f}%)"]
        if savings_rate < 20:
            lines.append("\n💡 Try saving at least 20% of your income.")
            if category_data:
                top = max(category_data, key=category_data.get)
                amt = category_data[top]
                lines.append(f"**{top}** is your biggest cost ({format_currency(amt)}). Cutting 10% saves {format_currency(amt*0.1)}!")
        lines.append("\n**50/30/20 Budget:**")
        lines.append(f"• Needs (50%): {format_currency(total_income*0.5)}")
        lines.append(f"• Wants (30%): {format_currency(total_income*0.3)}")
        lines.append(f"• Savings (20%): {format_currency(total_income*0.2)}")
        return "\n".join(lines)
    
    # Summary
    if any(w in q for w in ["summary", "overview", "report", "month"]):
        return (f"**📊 {date.today().strftime('%B %Y')} Summary**\n\n"
                f"**Income:** {format_currency(monthly['total_income'])}\n"
                f"**Expenses:** {format_currency(monthly['total_expense'])}\n"
                f"**Savings:** {format_currency(monthly['savings'])}\n"
                f"**Transactions:** {monthly['expense_count']} expenses, {monthly['income_count']} income\n"
                f"**Top Category:** {monthly['top_category']}")
    
    # Unusual spending
    if any(w in q for w in ["unusual", "pattern", "detect", "abnormal"]):
        unusual = AnalyticsService.detect_unusual_spending()
        if unusual:
            lines = ["🚨 **Unusual Spending Found:**"]
            for item in unusual:
                emoji = "⚠️ Higher" if item["type"] == "overspend" else "✅ Lower"
                lines.append(f"{emoji} **{item['category']}**: {abs(item['deviation']):.0f}% vs normal "
                             f"(Now: {format_currency(item['current'])}, Avg: {format_currency(item['average'])})")
            return "\n".join(lines)
        return "✅ No unusual patterns. Your spending looks consistent!"
    
    # Health score
    if any(w in q for w in ["health", "score", "rating"]):
        expense_ratio = (total_expenses / total_income * 100) if total_income > 0 else 100
        score = 100
        if expense_ratio > 80: score -= 30
        elif expense_ratio > 60: score -= 15
        elif expense_ratio > 40: score -= 5
        if len(category_data) <= 2: score -= 10
        if monthly['expense_count'] == 0: score -= 20
        score = max(0, min(100, score))
        
        rating = "🌟 Excellent!" if score >= 80 else "👍 Good!" if score >= 60 else "⚠️ Fair" if score >= 40 else "🚨 Needs attention"
        return (f"**🏆 Financial Health: {score}/100** {rating}\n\n"
                f"• Expense Ratio: {expense_ratio:.0f}%\n"
                f"• Active Categories: {len(category_data)}\n"
                f"• Monthly Transactions: {monthly['expense_count']}")
    
    # Food/category specific
    if any(w in q for w in ["food", "transport", "shopping", "entertainment", "health", "education", "bills"]):
        target = None
        for cat in ["Food", "Transport", "Shopping", "Entertainment", "Health", "Education", "Bills"]:
            if cat.lower() in q:
                target = cat
                break
        if target and target in category_data:
            amt = category_data[target]
            pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
            recent = ExpenseRepository.get_expenses_by_category(target)[:3]
            lines = [f"**📊 {target} Spending**",
                     f"Total: {format_currency(amt)} ({pct:.0f}% of all expenses)"]
            if recent:
                lines.append("\n**Recent:**")
                for e in recent:
                    lines.append(f"• {e.date}: {e.description} - {format_currency(e.amount)}")
            return "\n".join(lines)
        return f"Couldn't find spending data for that category."
    
    # Predictions
    if any(w in q for w in ["predict", "future", "forecast", "next month"]):
        df = AnalyticsService.get_expenses_dataframe()
        if not df.empty:
            months = len(df["month"].unique()) or 1
            avg = total_expenses / months
            diff = ((monthly['total_expense'] / avg) - 1) * 100 if avg > 0 else 0
            trend = f"⚠️ {diff:.0f}% higher" if diff > 0 else f"✅ {abs(diff):.0f}% lower"
            return (f"📊 **Spending Forecast**\n\n"
                    f"• Monthly Average: {format_currency(avg)}\n"
                    f"• Current Month: {format_currency(monthly['total_expense'])}\n"
                    f"• Trend: You're spending **{trend}** than average")
        return "Add some expenses first to get predictions!"
    
    # Default
    return (f"**💰 Your Finances at a Glance**\n\n"
            f"**Income:** {format_currency(total_income)}\n"
            f"**Expenses:** {format_currency(total_expenses)}\n"
            f"**Savings:** {format_currency(savings)} ({savings_rate:.0f}%)\n\n"
            f"💡 Try asking:\n"
            f"• \"Where am I spending the most?\"\n"
            f"• \"How can I save money?\"\n"
            f"• \"What's my financial health score?\"")