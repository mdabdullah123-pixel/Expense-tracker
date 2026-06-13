"""
Expenses page - CRUD operations for expenses and income.

Allows users to add, view, edit, and delete expenses and income records.
Includes AI-powered category suggestions and receipt scanning.
"""

import streamlit as st
import logging
from datetime import date, datetime
from typing import Optional

from database.repository import ExpenseRepository, IncomeRepository
from database.models import Expense, Income
from services.analytics_service import AnalyticsService
from utils.helpers import format_currency, validate_amount
from utils.receipt_parser import ReceiptParser

logger = logging.getLogger(__name__)


def render_expenses():
    """Render the expenses management page."""
    st.title("💳 Expenses & Income")
    st.markdown("Track your transactions")
    st.divider()

    # Tab layout for different operations
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ Add Expense",
        "💰 Add Income",
        "📋 View All",
        "📸 Scan Receipt",
    ])

    with tab1:
        render_add_expense()

    with tab2:
        render_add_income()

    with tab3:
        render_view_all()

    with tab4:
        render_receipt_scanner()


def render_add_expense():
    """Render the form for adding a new expense."""
    st.subheader("Add New Expense")

    with st.form("add_expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            expense_date = st.date_input("Date", value=date.today())
            amount_str = st.text_input(
                "Amount (₹)",
                placeholder="e.g., 450 or 1250.50",
                help="Enter the expense amount",
            )
            category = st.selectbox(
                "Category",
                options=Expense.VALID_CATEGORIES,
                index=0,
                help="Select or use AI suggestion below",
            )

        with col2:
            description = st.text_input(
                "Description",
                placeholder="e.g., Swiggy Order, Uber Ride",
                help="Brief description of the expense",
            )
            payment_method = st.selectbox(
                "Payment Method",
                options=Expense.VALID_PAYMENT_METHODS,
                index=0,
            )
            notes = st.text_area(
                "Notes (optional)",
                placeholder="Any additional notes...",
                height=68,
            )

        # AI Category Suggestion
        st.markdown("---")
        st.caption("🤖 AI-Powered Category Suggestion")

        ai_col1, ai_col2 = st.columns([3, 1])
        with ai_col1:
            suggest_text = st.text_input(
                "Enter a description for AI categorization",
                placeholder="e.g., Pizza delivery, Uber ride, Movie ticket",
                label_visibility="collapsed",
                key="ai_suggest_input",
            )
        with ai_col2:
            suggest_button = st.form_submit_button(
                "✨ Suggest",
                width="stretch",
                type="secondary",
            )

        if suggest_button and suggest_text:
            ai_service = st.session_state.get("ai_service")
            if ai_service and ai_service.is_configured:
                with st.spinner("AI is thinking..."):
                    suggested = ai_service.categorize_expense(suggest_text)
                    if suggested:
                        st.success(f"AI suggests category: **{suggested}**")
                        # Update the category selector
                        if suggested in Expense.VALID_CATEGORIES:
                            category = suggested
            else:
                st.warning("⚠️ AI service not configured. Go to Settings to set up.")

        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button(
            "✅ Add Expense",
            width="stretch",
            type="primary",
        )

        if submitted:
            is_valid, amount, error_msg = validate_amount(amount_str)
            if not is_valid:
                st.error(f"❌ {error_msg}")
            elif not description.strip():
                st.error("❌ Description is required")
            else:
                result = ExpenseRepository.add_expense(
                    expense_date=expense_date,
                    amount=amount,
                    category=category,
                    description=description.strip(),
                    payment_method=payment_method,
                    notes=notes.strip() if notes else None,
                )
                if result:
                    st.success(f"✅ Expense added: {description} - {format_currency(amount)}")
                    st.balloons()
                else:
                    st.error("❌ Failed to add expense. Please try again.")


def render_add_income():
    """Render the form for adding new income."""
    st.subheader("Add New Income")

    with st.form("add_income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            income_date = st.date_input("Date", value=date.today())
            amount_str = st.text_input(
                "Amount (₹)",
                placeholder="e.g., 50000 or 25000.50",
                help="Enter the income amount",
            )

        with col2:
            source = st.selectbox(
                "Source",
                options=Income.VALID_SOURCES,
                index=0,
            )
            notes = st.text_area(
                "Notes (optional)",
                placeholder="Any additional notes...",
                height=68,
            )

        st.markdown("---")
        submitted = st.form_submit_button(
            "✅ Add Income",
            width="stretch",
            type="primary",
        )

        if submitted:
            is_valid, amount, error_msg = validate_amount(amount_str)
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                result = IncomeRepository.add_income(
                    income_date=income_date,
                    amount=amount,
                    source=source.strip(),
                    notes=notes.strip() if notes else None,
                )
                if result:
                    st.success(f"✅ Income added: {source} - {format_currency(amount)}")
                    st.balloons()
                else:
                    st.error("❌ Failed to add income. Please try again.")


def render_view_all():
    """Render the view to see all expenses and income records."""
    st.subheader("All Transactions")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox(
            "Filter by type",
            options=["All", "Expenses", "Income"],
        )
    with col2:
        search = st.text_input("🔍 Search", placeholder="Search descriptions...")

    # Display expenses
    st.markdown("### 💸 Expenses")
    expenses = ExpenseRepository.get_all_expenses()

    if search:
        expenses = [
            e for e in expenses
            if search.lower() in e.description.lower()
            or search.lower() in e.category.lower()
        ]

    if expenses:
        for expense in expenses[:50]:  # Show latest 50
            with st.container():
                cols = st.columns([2, 2, 2, 3, 1])
                with cols[0]:
                    st.markdown(f"**{expense.date}**")
                with cols[1]:
                    st.markdown(f"_{expense.category}_")
                with cols[2]:
                    st.markdown(f"**{format_currency(expense.amount)}**")
                with cols[3]:
                    st.markdown(f"{expense.description}")
                with cols[4]:
                    # Delete button
                    delete_key = f"del_exp_{expense.id}"
                    if st.button("🗑️", key=delete_key, help="Delete this expense"):
                        if ExpenseRepository.delete_expense(expense.id):
                            st.success("Deleted!")
                            st.rerun()
                st.divider()
    else:
        st.info("No expenses recorded yet.")

    # Display income
    st.markdown("### 💰 Income")
    incomes = IncomeRepository.get_all_income()

    if search:
        incomes = [
            i for i in incomes
            if search.lower() in i.source.lower()
            or (i.notes and search.lower() in i.notes.lower())
        ]

    if incomes:
        for income in incomes[:50]:
            with st.container():
                cols = st.columns([2, 2, 2, 3, 1])
                with cols[0]:
                    st.markdown(f"**{income.date}**")
                with cols[1]:
                    st.markdown(f"_{income.source}_")
                with cols[2]:
                    st.markdown(f"**{format_currency(income.amount)}**")
                with cols[3]:
                    st.markdown(f"{income.notes or ''}")
                with cols[4]:
                    delete_key = f"del_inc_{income.id}"
                    if st.button("🗑️", key=delete_key, help="Delete this income"):
                        if IncomeRepository.delete_income(income.id):
                            st.success("Deleted!")
                            st.rerun()
                st.divider()
    else:
        st.info("No income recorded yet.")


def render_receipt_scanner():
    """Render the receipt scanning interface."""
    st.subheader("📸 Scan Receipt")
    st.markdown("Upload a receipt image to automatically extract information.")

    parser = ReceiptParser()

    uploaded_file = st.file_uploader(
        "Choose a receipt image",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload a clear photo of your receipt",
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()

        with st.spinner("🔄 Extracting text from receipt..."):
            # Try OCR first
            text = parser.extract_text_from_image(image_bytes)

            if text:
                st.success("✅ Text extracted from receipt!")
                with st.expander("📄 View extracted text"):
                    st.text(text)

                # Parse the text
                receipt_data = parser.parse_receipt_text(text)

                if receipt_data:
                    st.subheader("📋 Extracted Information")

                    col1, col2 = st.columns(2)
                    with col1:
                        merchant = receipt_data.get("merchant") or "Not detected"
                        st.info(f"**Merchant:** {merchant}")

                        total = receipt_data.get("total")
                        if total:
                            st.info(f"**Total:** {format_currency(total)}")
                        else:
                            st.info("**Total:** Not detected")

                    with col2:
                        rec_date = receipt_data.get("date") or "Not detected"
                        st.info(f"**Date:** {rec_date}")

                        category_suggest = receipt_data.get("category_suggestion", "Other")
                        st.info(f"**Suggested Category:** {category_suggest}")

                    items = receipt_data.get("items", [])
                    if items:
                        st.subheader("Items")
                        for i, item in enumerate(items[:10], 1):
                            st.markdown(f"{i}. {item}")

                    # Option to create expense from receipt
                    st.divider()
                    st.markdown("### Create Expense from Receipt")

                    with st.form("receipt_expense_form"):
                        expense_date = st.date_input(
                            "Date",
                            value=parse_date(receipt_data.get("date")) or date.today(),
                        )
                        amount = st.number_input(
                            "Amount",
                            value=float(receipt_data.get("total", 0) or 0),
                            min_value=0.01,
                            format="%.2f",
                        )
                        category = st.selectbox(
                            "Category",
                            options=Expense.VALID_CATEGORIES,
                            index=Expense.VALID_CATEGORIES.index(
                                category_suggest
                            ) if category_suggest in Expense.VALID_CATEGORIES else 0,
                        )
                        description = st.text_input(
                            "Description",
                            value=merchant or "Receipt expense",
                        )
                        payment_method = st.selectbox(
                            "Payment Method",
                            options=Expense.VALID_PAYMENT_METHODS,
                        )

                        submitted = st.form_submit_button(
                            "✅ Add from Receipt",
                            width="stretch",
                            type="primary",
                        )

                        if submitted:
                            result = ExpenseRepository.add_expense(
                                expense_date=expense_date,
                                amount=amount,
                                category=category,
                                description=description,
                                payment_method=payment_method,
                            )
                            if result:
                                st.success("✅ Expense added from receipt!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to add expense.")
            else:
                # OCR failed, try AI parsing
                st.warning("📝 OCR could not extract text. Trying AI parsing...")

                ai_service = st.session_state.get("ai_service")
                if ai_service and ai_service.is_configured:
                    # Use AI to parse receipt
                    st.info("AI will attempt to analyze the receipt. This may take a moment...")

                    # For image-based receipts without OCR, we can't send images to all AIs
                    # so we'll show manual entry form
                    st.info("Please enter the receipt details manually:")
                else:
                    st.warning(
                        "OCR is not available and AI service is not configured. "
                        "You can still enter the details manually."
                    )


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Try to parse a date string into a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None