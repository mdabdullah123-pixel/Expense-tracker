"""
Dashboard page - Main financial overview.

Displays key metrics (Total Income, Expenses, Savings) and interactive charts
using Plotly. Provides a quick summary of the user's financial health.
"""

import logging
from datetime import date

import streamlit as st

from services.analytics_service import AnalyticsService
from utils.charts import ChartBuilder
from utils.helpers import format_currency

logger = logging.getLogger(__name__)


def render_dashboard():
    """Render the main dashboard page."""
    st.title("📊 Dashboard")
    st.markdown("Your financial overview at a glance")
    st.divider()

    # Get summary data
    total_income = AnalyticsService.get_total_income()
    total_expenses = AnalyticsService.get_total_expenses()
    savings = total_income - total_expenses
    current_month = AnalyticsService.get_current_month_summary()

    # --- Key Metrics Cards ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total Income",
            value=format_currency(total_income),
            delta=f"+₹{current_month['total_income']:,.2f} this month",
        )

    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=format_currency(total_expenses),
            delta=f"₹{current_month['total_expense']:,.2f} this month",
            delta_color="inverse",
        )

    with col3:
        savings_color = "normal" if savings >= 0 else "inverse"
        delta_savings = current_month["savings"]
        st.metric(
            label="🏦 Total Savings",
            value=format_currency(savings),
            delta=f"{'+' if delta_savings >= 0 else ''}₹{delta_savings:,.2f} this month",
            delta_color=savings_color,
        )

    with col4:
        st.metric(
            label="📈 Top Category",
            value=current_month["top_category"],
            delta=f"{current_month['expense_count']} transactions",
        )

    st.divider()

    # --- Charts Section ---
    left_col, right_col = st.columns(2)

    with left_col:
        # Category spending pie chart
        st.subheader("🥧 Spending by Category")
        category_data = AnalyticsService.get_category_breakdown()
        fig_pie = ChartBuilder.create_category_pie_chart(category_data)
        st.plotly_chart(fig_pie, width="stretch", key="dashboard_category_pie_chart")

    with right_col:
        # Top categories bar chart
        st.subheader("📊 Top Spending Categories")
        top_categories = AnalyticsService.get_top_categories(5)
        fig_top = ChartBuilder.create_top_categories_chart(top_categories)
        st.plotly_chart(fig_top, width="stretch", key="dashboard_top_categories_chart")

    # Second row of charts
    col1, col2 = st.columns(2)

    with col1:
        # Monthly spending line chart
        st.subheader("📈 Monthly Spending Trend")
        year = date.today().year
        monthly_expense = AnalyticsService.get_monthly_spending(year)
        fig_line = ChartBuilder.create_monthly_spending_chart(
            monthly_expense,
            title=f"Expenses in {year}",
        )
        st.plotly_chart(
            fig_line,
            width="stretch",
            key="dashboard_monthly_spending_chart",
        )

    with col2:
        # Income vs Expense bar chart
        st.subheader("📊 Income vs Expenses")
        monthly_income = AnalyticsService.get_monthly_income(year)
        fig_bar = ChartBuilder.create_income_vs_expense_chart(
            monthly_expense, monthly_income
        )
        st.plotly_chart(
            fig_bar,
            width="stretch",
            key="dashboard_income_vs_expense_chart",
        )

    # --- Recent Transactions ---
    st.divider()
    st.subheader("📋 Recent Expenses")

    expense_df = AnalyticsService.get_expenses_dataframe()
    if not expense_df.empty:
        display_df = expense_df.head(10)[
            ["date", "amount", "category", "description", "payment_method"]
        ]
        display_df["date"] = display_df["date"].astype(str)
        display_df["amount"] = display_df["amount"].apply(lambda x: format_currency(x))
        display_df.columns = [
            "Date",
            "Amount",
            "Category",
            "Description",
            "Payment Method",
        ]
        st.dataframe(display_df, width="stretch")
    else:
        st.info(
            "No expenses recorded yet. Add your first expense in the Expenses page."
        )

    # --- Unusual Spending Alerts ---
    st.divider()
    st.subheader("🚨 Spending Alerts")

    unusual = AnalyticsService.detect_unusual_spending()
    if unusual:
        for item in unusual:
            if item["type"] == "overspend":
                st.warning(
                    f"⚠️ **{item['category']}** spending is **{item['deviation']:.0f}% higher** "
                    f"than usual! Current: {format_currency(item['current'])} "
                    f"vs Average: {format_currency(item['average'])}"
                )
            else:
                st.success(
                    f"✅ **{item['category']}** spending is **{abs(item['deviation']):.0f}% lower** "
                    f"than usual! Current: {format_currency(item['current'])} "
                    f"vs Average: {format_currency(item['average'])}"
                )
    else:
        st.info(
            "No unusual spending patterns detected. Add more data for better insights."
        )
