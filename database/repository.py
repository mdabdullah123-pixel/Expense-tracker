"""
Repository pattern implementation for database operations.

Provides clean CRUD interfaces for Expense, Income, and Settings models.
All database operations use SQLAlchemy sessions with proper error handling,
input validation, and SQL injection protection via parameterized queries.
"""

import logging
from datetime import date

from sqlalchemy import desc, extract, func
from sqlalchemy.orm import Session

from database.db import close_session, get_db_session
from database.models import Expense, Income, Settings

logger = logging.getLogger(__name__)


class ExpenseRepository:
    """Repository for Expense CRUD operations."""

    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return get_db_session()

    @staticmethod
    def add_expense(
        expense_date: date,
        amount: float,
        category: str,
        description: str,
        payment_method: str = "Cash",
        notes: str | None = None,
    ) -> Expense | None:
        """
        Add a new expense to the database.

        Args:
            expense_date: Date of the expense
            amount: Monetary amount (must be positive)
            category: Expense category (validated against predefined list)
            description: Brief description
            payment_method: Payment method used
            notes: Optional additional notes

        Returns:
            Expense object if successful, None otherwise
        """
        session = ExpenseRepository.get_session()
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Amount must be positive")

            # Validate category
            if category not in Expense.VALID_CATEGORIES:
                raise ValueError(f"Invalid category: {category}")

            expense = Expense(
                date=expense_date,
                amount=amount,
                category=category,
                description=description.strip(),
                payment_method=payment_method,
                notes=notes.strip() if notes else None,
            )
            session.add(expense)
            session.commit()
            logger.info("Expense added: %s - ₹%.2f (%s)", description, amount, category)
            return expense
        except Exception as e:
            session.rollback()
            logger.error("Failed to add expense: %s", str(e))
            return None
        finally:
            close_session(session)

    @staticmethod
    def get_all_expenses() -> list[Expense]:
        """
        Retrieve all expenses ordered by date descending.

        Returns:
            List of Expense objects
        """
        session = ExpenseRepository.get_session()
        try:
            return session.query(Expense).order_by(desc(Expense.date)).all()
        except Exception as e:
            logger.error("Failed to fetch expenses: %s", str(e))
            return []
        finally:
            close_session(session)

    @staticmethod
    def get_expense_by_id(expense_id: int) -> Expense | None:
        """
        Retrieve a single expense by ID.

        Args:
            expense_id: The expense ID to look up

        Returns:
            Expense object if found, None otherwise
        """
        session = ExpenseRepository.get_session()
        try:
            return session.query(Expense).filter(Expense.id == expense_id).first()
        except Exception as e:
            logger.error("Failed to fetch expense %d: %s", expense_id, str(e))
            return None
        finally:
            close_session(session)

    @staticmethod
    def update_expense(
        expense_id: int,
        expense_date: date | None = None,
        amount: float | None = None,
        category: str | None = None,
        description: str | None = None,
        payment_method: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """
        Update an existing expense.

        Args:
            expense_id: ID of expense to update
            expense_date: New date (optional)
            amount: New amount (optional, must be positive)
            category: New category (optional)
            description: New description (optional)
            payment_method: New payment method (optional)
            notes: New notes (optional)

        Returns:
            True if successful, False otherwise
        """
        session = ExpenseRepository.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if not expense:
                logger.warning("Expense %d not found", expense_id)
                return False

            if expense_date is not None:
                expense.date = expense_date
            if amount is not None:
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                expense.amount = amount
            if category is not None:
                if category not in Expense.VALID_CATEGORIES:
                    raise ValueError(f"Invalid category: {category}")
                expense.category = category
            if description is not None:
                expense.description = description.strip()
            if payment_method is not None:
                expense.payment_method = payment_method
            if notes is not None:
                expense.notes = notes.strip()

            session.commit()
            logger.info("Expense %d updated", expense_id)
            return True
        except Exception as e:
            session.rollback()
            logger.error("Failed to update expense %d: %s", expense_id, str(e))
            return False
        finally:
            close_session(session)

    @staticmethod
    def delete_expense(expense_id: int) -> bool:
        """
        Delete an expense by ID.

        Args:
            expense_id: ID of expense to delete

        Returns:
            True if successful, False otherwise
        """
        session = ExpenseRepository.get_session()
        try:
            expense = session.query(Expense).filter(Expense.id == expense_id).first()
            if not expense:
                logger.warning("Expense %d not found for deletion", expense_id)
                return False

            session.delete(expense)
            session.commit()
            logger.info("Expense %d deleted", expense_id)
            return True
        except Exception as e:
            session.rollback()
            logger.error("Failed to delete expense %d: %s", expense_id, str(e))
            return False
        finally:
            close_session(session)

    @staticmethod
    def get_expenses_by_date_range(start_date: date, end_date: date) -> list[Expense]:
        """
        Get expenses within a date range.

        Args:
            start_date: Start of range (inclusive)
            end_date: End of range (inclusive)

        Returns:
            List of Expense objects
        """
        session = ExpenseRepository.get_session()
        try:
            return (
                session.query(Expense)
                .filter(Expense.date >= start_date, Expense.date <= end_date)
                .order_by(desc(Expense.date))
                .all()
            )
        except Exception as e:
            logger.error("Failed to fetch expenses by date range: %s", str(e))
            return []
        finally:
            close_session(session)

    @staticmethod
    def get_expenses_by_category(category: str) -> list[Expense]:
        """
        Get all expenses for a specific category.

        Args:
            category: Category to filter by

        Returns:
            List of Expense objects
        """
        session = ExpenseRepository.get_session()
        try:
            return (
                session.query(Expense)
                .filter(Expense.category == category)
                .order_by(desc(Expense.date))
                .all()
            )
        except Exception as e:
            logger.error("Failed to fetch expenses by category: %s", str(e))
            return []
        finally:
            close_session(session)

    @staticmethod
    def get_total_expenses() -> float:
        """
        Calculate total of all expenses.

        Returns:
            Total expense amount as float
        """
        session = ExpenseRepository.get_session()
        try:
            result = session.query(func.sum(Expense.amount)).scalar()
            return float(result) if result else 0.0
        except Exception as e:
            logger.error("Failed to calculate total expenses: %s", str(e))
            return 0.0
        finally:
            close_session(session)

    @staticmethod
    def get_monthly_summary(year: int, month: int) -> dict:
        """
        Get expense summary for a specific month.

        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Dictionary with total, count, and category breakdown
        """
        session = ExpenseRepository.get_session()
        try:
            expenses = (
                session.query(Expense)
                .filter(
                    extract("year", Expense.date) == year,
                    extract("month", Expense.date) == month,
                )
                .all()
            )

            total = sum(e.amount for e in expenses)
            category_breakdown: dict[str, float] = {}
            for expense in expenses:
                cat = expense.category
                category_breakdown[cat] = (
                    category_breakdown.get(cat, 0) + expense.amount
                )

            return {
                "total": total,
                "count": len(expenses),
                "category_breakdown": category_breakdown,
                "expenses": expenses,
            }
        except Exception as e:
            logger.error("Failed to get monthly summary: %s", str(e))
            return {"total": 0, "count": 0, "category_breakdown": {}, "expenses": []}
        finally:
            close_session(session)

    @staticmethod
    def get_category_totals(
        start_date: date | None = None, end_date: date | None = None
    ) -> list[tuple[str, float]]:
        """
        Get total spending per category, optionally filtered by date range.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of (category, total_amount) tuples
        """
        session = ExpenseRepository.get_session()
        try:
            query = session.query(
                Expense.category, func.sum(Expense.amount).label("total")
            )

            if start_date:
                query = query.filter(Expense.date >= start_date)
            if end_date:
                query = query.filter(Expense.date <= end_date)

            results = query.group_by(Expense.category).order_by(desc("total")).all()
            return [(r.category, float(r.total)) for r in results]
        except Exception as e:
            logger.error("Failed to get category totals: %s", str(e))
            return []
        finally:
            close_session(session)


class IncomeRepository:
    """Repository for Income CRUD operations."""

    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return get_db_session()

    @staticmethod
    def add_income(
        income_date: date,
        amount: float,
        source: str,
        notes: str | None = None,
    ) -> Income | None:
        """
        Add a new income record.

        Args:
            income_date: Date income was received
            amount: Monetary amount (must be positive)
            source: Source of income
            notes: Optional notes

        Returns:
            Income object if successful, None otherwise
        """
        session = IncomeRepository.get_session()
        try:
            if amount <= 0:
                raise ValueError("Amount must be positive")

            income = Income(
                date=income_date,
                amount=amount,
                source=source.strip(),
                notes=notes.strip() if notes else None,
            )
            session.add(income)
            session.commit()
            logger.info("Income added: %s - ₹%.2f", source, amount)
            return income
        except Exception as e:
            session.rollback()
            logger.error("Failed to add income: %s", str(e))
            return None
        finally:
            close_session(session)

    @staticmethod
    def get_all_income() -> list[Income]:
        """
        Retrieve all income records ordered by date descending.

        Returns:
            List of Income objects
        """
        session = IncomeRepository.get_session()
        try:
            return session.query(Income).order_by(desc(Income.date)).all()
        except Exception as e:
            logger.error("Failed to fetch income: %s", str(e))
            return []
        finally:
            close_session(session)

    @staticmethod
    def get_income_by_id(income_id: int) -> Income | None:
        """
        Retrieve a single income record by ID.

        Args:
            income_id: The income ID to look up

        Returns:
            Income object if found, None otherwise
        """
        session = IncomeRepository.get_session()
        try:
            return session.query(Income).filter(Income.id == income_id).first()
        except Exception as e:
            logger.error("Failed to fetch income %d: %s", income_id, str(e))
            return None
        finally:
            close_session(session)

    @staticmethod
    def update_income(
        income_id: int,
        income_date: date | None = None,
        amount: float | None = None,
        source: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """
        Update an existing income record.

        Args:
            income_id: ID of income to update
            income_date: New date (optional)
            amount: New amount (optional)
            source: New source (optional)
            notes: New notes (optional)

        Returns:
            True if successful, False otherwise
        """
        session = IncomeRepository.get_session()
        try:
            income = session.query(Income).filter(Income.id == income_id).first()
            if not income:
                logger.warning("Income %d not found", income_id)
                return False

            if income_date is not None:
                income.date = income_date
            if amount is not None:
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                income.amount = amount
            if source is not None:
                income.source = source.strip()
            if notes is not None:
                income.notes = notes.strip() if notes else None

            session.commit()
            logger.info("Income %d updated", income_id)
            return True
        except Exception as e:
            session.rollback()
            logger.error("Failed to update income %d: %s", income_id, str(e))
            return False
        finally:
            close_session(session)

    @staticmethod
    def delete_income(income_id: int) -> bool:
        """
        Delete an income record by ID.

        Args:
            income_id: ID of income to delete

        Returns:
            True if successful, False otherwise
        """
        session = IncomeRepository.get_session()
        try:
            income = session.query(Income).filter(Income.id == income_id).first()
            if not income:
                logger.warning("Income %d not found for deletion", income_id)
                return False

            session.delete(income)
            session.commit()
            logger.info("Income %d deleted", income_id)
            return True
        except Exception as e:
            session.rollback()
            logger.error("Failed to delete income %d: %s", income_id, str(e))
            return False
        finally:
            close_session(session)

    @staticmethod
    def get_income_by_date_range(start_date: date, end_date: date) -> list[Income]:
        """
        Get income records within a date range.

        Args:
            start_date: Start of range (inclusive)
            end_date: End of range (inclusive)

        Returns:
            List of Income objects
        """
        session = IncomeRepository.get_session()
        try:
            return (
                session.query(Income)
                .filter(Income.date >= start_date, Income.date <= end_date)
                .order_by(desc(Income.date))
                .all()
            )
        except Exception as e:
            logger.error("Failed to fetch income by date range: %s", str(e))
            return []
        finally:
            close_session(session)

    @staticmethod
    def get_total_income() -> float:
        """
        Calculate total of all income.

        Returns:
            Total income amount as float
        """
        session = IncomeRepository.get_session()
        try:
            result = session.query(func.sum(Income.amount)).scalar()
            return float(result) if result else 0.0
        except Exception as e:
            logger.error("Failed to calculate total income: %s", str(e))
            return 0.0
        finally:
            close_session(session)


class SettingsRepository:
    """Repository for application settings."""

    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return get_db_session()

    @staticmethod
    def get_settings() -> Settings | None:
        """
        Get the current application settings.
        Returns the first settings record or None.

        Returns:
            Settings object or None
        """
        session = SettingsRepository.get_session()
        try:
            return session.query(Settings).first()
        except Exception as e:
            logger.error("Failed to fetch settings: %s", str(e))
            return None
        finally:
            close_session(session)

    @staticmethod
    def save_settings(provider: str, model: str, api_key: str | None = None) -> bool:
        """
        Save or update application settings.

        Args:
            provider: AI provider name
            model: Model name for the provider
            api_key: Optional API key (for cloud providers)

        Returns:
            True if successful, False otherwise
        """
        session = SettingsRepository.get_session()
        try:
            settings = session.query(Settings).first()
            if settings:
                settings.provider = provider
                settings.model = model
                if api_key is not None:
                    settings.api_key = api_key
            else:
                settings = Settings(
                    provider=provider,
                    model=model,
                    api_key=api_key,
                )
                session.add(settings)
            session.commit()
            logger.info("Settings saved: provider=%s, model=%s", provider, model)
            return True
        except Exception as e:
            session.rollback()
            logger.error("Failed to save settings: %s", str(e))
            return False
        finally:
            close_session(session)
