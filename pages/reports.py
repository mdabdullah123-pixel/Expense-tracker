"""
Reports page - AI-powered financial reports.

Generates weekly and monthly spending reports using AI.
Reports include spending trends, financial health scores,
budget recommendations, and savings suggestions.
Reports can be downloaded as markdown files.
"""
  
import streamlit as st
import logging
from datetime import date, timedelta

from services.analytics_service import AnalyticsService
from utils.helpers import format_currency

logger = logging.getLogger(__name__)


def render_reports():
    """Render the AI-powered reports page."""
    st.title("📑 AI Spending Reports")
    st.markdown("Generate intelligent financial reports powered by AI")
    st.divider()

    # Check if AI is configured
    ai_service = st.session_state.get("ai_service")
    ai_available = ai_service and ai_service.is_configured

    if not ai_available:
        st.warning(
            "⚠️ **AI service not configured.** "
            "Please go to the **Settings** page to configure an AI provider "
            "for AI-powered reports."
        )
        st.info("You can still view non-AI reports below.")

    # Report type selection
    report_type = st.radio(
        "Select Report Type",
        options=["📈 Monthly Report", "📊 Weekly Report"],
        horizontal=True,
        help="Choose the type of report to generate",
    )

    is_monthly = report_type == "📈 Monthly Report"

    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        if is_monthly:
            selected_month = st.selectbox(
                "Select Month",
                options=list(range(1, 13)),
                format_func=lambda m: [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][m - 1],
                index=date.today().month - 1,
            )
            selected_year = st.number_input(
                "Year",
                min_value=2020,
                max_value=2030,
                value=date.today().year,
            )
            start_date = date(selected_year, selected_month, 1)
            end_date = date.today()
        else:
            # Current week
            today = date.today()
            start_date = today - timedelta(days=today.weekday())
            end_date = today
            st.info(f"**Week:** {start_date} to {end_date}")

    # Generate reports
    st.divider()
    st.subheader("📊 Financial Summary")

    # Get data for the period
    expense_df = AnalyticsService.get_expenses_dataframe(start_date, end_date)
    income_df = AnalyticsService.get_income_dataframe(start_date, end_date)

    total_expenses = float(expense_df["amount"].sum()) if not expense_df.empty else 0.0
    total_income = float(income_df["amount"].sum()) if not income_df.empty else 0.0
    savings = total_income - total_expenses

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "💰 Total Income",
            format_currency(total_income),
            help="Total income for the period",
        )
    with col2:
        st.metric(
            "💸 Total Expenses",
            format_currency(total_expenses),
            delta=f"-{format_currency(total_expenses)}",
            delta_color="inverse",
            help="Total expenses for the period",
        )
    with col3:
        savings_color = "normal" if savings >= 0 else "inverse"
        st.metric(
            "🏦 Savings",
            format_currency(savings),
            delta=f"{'+' if savings >= 0 else ''}{format_currency(savings)}",
            delta_color=savings_color,
            help="Income minus expenses",
        )

    # Category breakdown
    if not expense_df.empty:
        st.subheader("📊 Category Breakdown")
        category_totals = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)

        for cat, amt in category_totals.items():
            pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
            cols = st.columns([2, 1, 3])
            with cols[0]:
                st.markdown(f"**{cat}**")
            with cols[1]:
                st.markdown(f"{format_currency(amt)}")
            with cols[2]:
                st.progress(pct / 100, text=f"{pct:.1f}%")

    # Recent transactions
    if not expense_df.empty:
        st.subheader("📋 Recent Transactions")
        recent = expense_df.head(10)
        for _, row in recent.iterrows():
            st.markdown(
                f"- **{row['date']}** | {row['category']} | "
                f"{format_currency(row['amount'])} | {row['description']}"
            )

    # AI-Powered Report
    st.divider()
    st.subheader("🤖 AI-Powered Insights")

    if ai_available:
        if st.button(
            f"✨ Generate {'Monthly' if is_monthly else 'Weekly'} AI Report",
            use_container_width=True,
            type="primary",
        ):
            with st.spinner("🧠 AI is analyzing your spending data..."):
                # Build data context
                data_context = AnalyticsService.build_ai_context()

                # Add period-specific context
                period_info = (
                    f"Report Period: {start_date} to {end_date}\n"
                    f"Period Expenses: ₹{total_expenses:.2f}\n"
                    f"Period Income: ₹{total_income:.2f}\n"
                    f"Period Savings: ₹{savings:.2f}\n"
                )
                full_context = period_info + "\n" + data_context

                # Generate report
                report_type_str = "monthly" if is_monthly else "weekly"
                report = ai_service.generate_report(report_type_str, full_context)

                if report:
                    st.markdown("---")
                    st.markdown(report)

                    # Download button
                    report_filename = f"{report_type_str}_report_{date.today().isoformat()}.md"
                    st.download_button(
                        label="📥 Download Report (Markdown)",
                        data=report,
                        file_name=report_filename,
                        mime="text/markdown",
                        use_container_width=True,
                    )
                else:
                    st.error("❌ Failed to generate AI report. Please try again.")
    else:
        st.info(
            "💡 Configure an AI provider in **Settings** to unlock AI-powered "
            "reports with personalized financial insights and recommendations."
        )

    # Budget Suggestions (Non-AI)
    st.divider()
    st.subheader("💡 Smart Savings Tips")

    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    tips = []
    if savings_rate < 10:
        tips.append("🚨 **Low savings rate detected.** Try to save at least 20% of your income.")
    if not expense_df.empty:
        top_cat = expense_df.groupby("category")["amount"].sum().idxmax()
        tips.append(f"📌 **{top_cat}** is your highest expense category. "
                     f"Consider if there are ways to reduce this spending.")
    if total_expenses > total_income:
        tips.append("⚠️ **Expenses exceed income!** Review your spending and "
                     "look for areas to cut back.")

    if tips:
        for tip in tips:
            st.markdown(tip)
    else:
        st.success("✅ Your spending habits look healthy!")