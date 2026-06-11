"""
Analytics Service - Computes financial analytics and insights.

Provides methods for calculating financial summaries, spending patterns,
and generating data contexts for AI-powered analysis.
All calculations use pandas for efficient data processing.
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional
import pandas as pd

from database.repository import ExpenseRepository, IncomeRepository
from database.models import Expense, Income

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for computing financial analytics and insights.
    
    Provides methods to calculate totals, generate summaries,
    identify spending patterns, and prepare data for AI analysis.
    """
    
    @staticmethod
    def get_total_expenses() -> float:
        """Get total expenses across all records."""
        return ExpenseRepository.get_total_expenses()
    
    @staticmethod
    def get_total_income() -> float:
        """Get total income across all records."""
        return IncomeRepository.get_total_income()
    
    @staticmethod
    def get_savings() -> float:
        """Calculate total savings (income - expenses)."""
        return IncomeRepository.get_total_income() - ExpenseRepository.get_total_expenses()
    
    @staticmethod
    def get_expenses_dataframe(start_date: Optional[date] = None, end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get expenses as a pandas DataFrame for analysis.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame with expense data
        """
        if start_date and end_date:
            expenses = ExpenseRepository.get_expenses_by_date_range(start_date, end_date)
        else:
            expenses = ExpenseRepository.get_all_expenses()
        
        if not expenses:
            return pd.DataFrame(columns=["date", "amount", "category", "description", "payment_method"])
        
        data = [
            {
                "date": e.date,
                "amount": e.amount,
                "category": e.category,
                "description": e.description,
                "payment_method": e.payment_method,
                "month": e.date.month if e.date else None,
                "year": e.date.year if e.date else None,
            }
            for e in expenses
        ]
        return pd.DataFrame(data)
    
    @staticmethod
    def get_income_dataframe(start_date: Optional[date] = None, end_date: Optional[date] = None) -> pd.DataFrame:
        """
        Get income as a pandas DataFrame for analysis.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            DataFrame with income data
        """
        if start_date and end_date:
            incomes = IncomeRepository.get_income_by_date_range(start_date, end_date)
        else:
            incomes = IncomeRepository.get_all_income()
        
        if not incomes:
            return pd.DataFrame(columns=["date", "amount", "source"])
        
        data = [
            {
                "date": i.date,
                "amount": i.amount,
                "source": i.source,
                "month": i.date.month if i.date else None,
                "year": i.date.year if i.date else None,
            }
            for i in incomes
        ]
        return pd.DataFrame(data)
    
    @staticmethod
    def get_monthly_spending(year: Optional[int] = None) -> pd.DataFrame:
        """
        Get monthly spending breakdown.
        
        Args:
            year: Year to filter by (defaults to current year)
            
        Returns:
            DataFrame with monthly spending totals
        """
        if year is None:
            year = date.today().year
        
        df = AnalyticsService.get_expenses_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["month", "total"])
        
        df = df[df["year"] == year]
        if df.empty:
            return pd.DataFrame(columns=["month", "total"])
        
        monthly = df.groupby("month")["amount"].sum().reset_index()
        monthly.columns = ["month", "total"]
        return monthly.sort_values("month")
    
    @staticmethod
    def get_monthly_income(year: Optional[int] = None) -> pd.DataFrame:
        """
        Get monthly income breakdown.
        
        Args:
            year: Year to filter by (defaults to current year)
            
        Returns:
            DataFrame with monthly income totals
        """
        if year is None:
            year = date.today().year
        
        df = AnalyticsService.get_income_dataframe()
        if df.empty:
            return pd.DataFrame(columns=["month", "total"])
        
        df = df[df["year"] == year]
        if df.empty:
            return pd.DataFrame(columns=["month", "total"])
        
        monthly = df.groupby("month")["amount"].sum().reset_index()
        monthly.columns = ["month", "total"]
        return monthly.sort_values("month")
    
    @staticmethod
    def get_category_breakdown(start_date: Optional[date] = None, end_date: Optional[date] = None) -> dict:
        """
        Get spending breakdown by category.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict mapping category -> total amount
        """
        totals = ExpenseRepository.get_category_totals(start_date, end_date)
        return {cat: amt for cat, amt in totals}
    
    @staticmethod
    def get_top_categories(limit: int = 5) -> List[tuple]:
        """
        Get top spending categories.
        
        Args:
            limit: Number of top categories to return
            
        Returns:
            List of (category, amount) tuples sorted by amount descending
        """
        totals = ExpenseRepository.get_category_totals()
        return totals[:limit]
    
    @staticmethod
    def get_current_month_summary() -> dict:
        """
        Get a summary of the current month's finances.
        
        Returns:
            Dictionary with total_expense, total_income, savings, 
            top_category, and transaction_count
        """
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        expense_df = AnalyticsService.get_expenses_dataframe(start_of_month, today)
        income_df = AnalyticsService.get_income_dataframe(start_of_month, today)
        
        total_expense = float(expense_df["amount"].sum()) if not expense_df.empty else 0.0
        total_income = float(income_df["amount"].sum()) if not income_df.empty else 0.0
        
        top_category = "N/A"
        if not expense_df.empty:
            category_totals = expense_df.groupby("category")["amount"].sum()
            if not category_totals.empty:
                top_category = category_totals.idxmax()
        
        return {
            "total_expense": round(total_expense, 2),
            "total_income": round(total_income, 2),
            "savings": round(total_income - total_expense, 2),
            "top_category": top_category,
            "expense_count": len(expense_df),
            "income_count": len(income_df),
        }
    
    @staticmethod
    def get_weekly_expenses() -> pd.DataFrame:
        """
        Get expenses for the current week.
        
        Returns:
            DataFrame with current week's expenses
        """
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        return AnalyticsService.get_expenses_dataframe(start_of_week, today)
    
    @staticmethod
    def build_ai_context() -> str:
        """
        Build a formatted text context of user's financial data for AI analysis.
        
        Returns:
            Formatted string with expense and income data summary
        """
        context_parts = []
        
        # Overall summary
        total_expenses = AnalyticsService.get_total_expenses()
        total_income = AnalyticsService.get_total_income()
        savings = total_income - total_expenses
        
        context_parts.append("=== FINANCIAL OVERVIEW ===")
        context_parts.append(f"Total Expenses: ₹{total_expenses:.2f}")
        context_parts.append(f"Total Income: ₹{total_income:.2f}")
        context_parts.append(f"Net Savings: ₹{savings:.2f}")
        context_parts.append("")
        
        # Current month summary
        current = AnalyticsService.get_current_month_summary()
        context_parts.append("=== CURRENT MONTH ===")
        context_parts.append(f"Month Expenses: ₹{current['total_expense']:.2f}")
        context_parts.append(f"Month Income: ₹{current['total_income']:.2f}")
        context_parts.append(f"Month Savings: ₹{current['savings']:.2f}")
        context_parts.append(f"Top Category: {current['top_category']}")
        context_parts.append(f"Expense Count: {current['expense_count']}")
        context_parts.append("")
        
        # Category breakdown
        category_data = AnalyticsService.get_category_breakdown()
        if category_data:
            context_parts.append("=== SPENDING BY CATEGORY ===")
            for cat, amt in sorted(category_data.items(), key=lambda x: x[1], reverse=True):
                pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
                context_parts.append(f"{cat}: ₹{amt:.2f} ({pct:.1f}%)")
            context_parts.append("")
        
        # Recent transactions
        expenses = ExpenseRepository.get_all_expenses()
        recent = expenses[:10]
        if recent:
            context_parts.append("=== RECENT TRANSACTIONS (Last 10) ===")
            for e in recent:
                context_parts.append(
                    f"{e.date}: ₹{e.amount:.2f} - {e.description} [{e.category}]"
                )
        
        return "\n".join(context_parts)
    
    @staticmethod
    def detect_unusual_spending() -> List[dict]:
        """
        Detect potentially unusual spending patterns.
        
        Compares current month spending against historical averages
        and flags categories with significant deviations.
        
        Returns:
            List of dicts with category, current, average, and deviation %
        """
        today = date.today()
        current_month_start = date(today.year, today.month, 1)
        
        # Get current month expenses
        current_df = AnalyticsService.get_expenses_dataframe(current_month_start, today)
        
        # Get historical expenses (last 3 months)
        three_months_ago = current_month_start - timedelta(days=90)
        historical_df = AnalyticsService.get_expenses_dataframe(three_months_ago, current_month_start)
        
        unusual = []
        
        if current_df.empty or historical_df.empty:
            return unusual
        
        # Current month per-category totals
        current_cat = current_df.groupby("category")["amount"].sum()
        
        # Historical monthly average per category
        historical_df["year_month"] = historical_df["year"].astype(str) + "-" + historical_df["month"].astype(str)
        historical_monthly = historical_df.groupby(["year_month", "category"])["amount"].sum().reset_index()
        historical_avg = historical_monthly.groupby("category")["amount"].mean()
        
        for cat in current_cat.index:
            if cat in historical_avg.index and historical_avg[cat] > 0:
                current_amt = current_cat[cat]
                avg_amt = historical_avg[cat]
                deviation = ((current_amt - avg_amt) / avg_amt) * 100
                
                if abs(deviation) > 50:  # Flag if >50% deviation
                    unusual.append({
                        "category": cat,
                        "current": round(current_amt, 2),
                        "average": round(avg_amt, 2),
                        "deviation": round(deviation, 1),
                        "type": "overspend" if deviation > 0 else "underspend",
                    })
        
        return unusual[:5]  # Return top 5 unusual patterns