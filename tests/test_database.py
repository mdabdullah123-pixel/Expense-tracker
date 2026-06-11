"""
Unit tests for database models and repository operations.

Tests CRUD operations for expenses, income, and settings
with proper setup and teardown using an in-memory SQLite database.
"""

import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Expense, Income, Settings
from database.repository import ExpenseRepository, IncomeRepository, SettingsRepository
from database.db import get_db_session


class TestExpenseModel:
    """Test the Expense model and repository."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Set up in-memory database for testing."""
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        
        # Override get_engine to return test engine
        import database.db as db_module
        self._original_get_engine = db_module.get_engine
        db_module.get_engine = lambda: self.engine
        
        yield
        
        # Clean up
        db_module.get_engine = self._original_get_engine

    def test_expense_model_creation(self):
        """Test creating a new expense model instance."""
        expense = Expense(
            date=date(2024, 1, 15),
            amount=450.00,
            category="Food",
            description="Swiggy Order",
            payment_method="UPI",
        )
        assert expense.amount == 450.00
        assert expense.category == "Food"
        assert expense.description == "Swiggy Order"
        assert expense.to_dict() is not None

    def test_expense_repository_add(self):
        """Test adding expense via repository."""
        ExpenseRepository.add_expense(
            expense_date=date(2024, 1, 15),
            amount=250.00,
            category="Transport",
            description="Uber Ride",
            payment_method="UPI",
        )
        # Verify it was saved by fetching it back
        expenses = ExpenseRepository.get_all_expenses()
        assert len(expenses) == 1
        assert expenses[0].amount == 250.00

    def test_expense_repository_add_invalid_amount(self):
        """Test adding expense with invalid amount."""
        result = ExpenseRepository.add_expense(
            expense_date=date(2024, 1, 15),
            amount=-100,
            category="Food",
            description="Test",
        )
        assert result is None

    def test_expense_repository_get_all(self):
        """Test retrieving all expenses."""
        ExpenseRepository.add_expense(date(2024, 1, 15), 100, "Food", "Test 1")
        ExpenseRepository.add_expense(date(2024, 1, 16), 200, "Transport", "Test 2")

        expenses = ExpenseRepository.get_all_expenses()
        assert len(expenses) == 2

    def test_expense_repository_delete(self):
        """Test deleting an expense."""
        # Add expense and get its id via query
        ExpenseRepository.add_expense(
            date(2024, 1, 15), 100, "Food", "To Delete"
        )
        expenses = ExpenseRepository.get_all_expenses()
        assert len(expenses) == 1
        expense_id = expenses[0].id

        deleted = ExpenseRepository.delete_expense(expense_id)
        assert deleted is True

        fetched = ExpenseRepository.get_expense_by_id(expense_id)
        assert fetched is None

    def test_expense_valid_categories(self):
        """Test valid expense categories."""
        valid = Expense.VALID_CATEGORIES
        assert "Food" in valid
        assert "Transport" in valid
        assert "Entertainment" in valid
        assert "Other" in valid
        assert len(valid) == 10


class TestIncomeModel:
    """Test the Income model and repository."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Set up in-memory database for testing."""
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        
        import database.db as db_module
        self._original_get_engine = db_module.get_engine
        db_module.get_engine = lambda: self.engine
        
        yield
        
        db_module.get_engine = self._original_get_engine

    def test_income_model_creation(self):
        """Test creating a new income model instance."""
        income = Income(
            date=date(2024, 1, 1),
            amount=50000.00,
            source="Salary",
        )
        assert income.amount == 50000.00
        assert income.source == "Salary"
        assert income.to_dict() is not None

    def test_income_repository(self):
        """Test income repository operations."""
        result = IncomeRepository.add_income(
            income_date=date(2024, 1, 1),
            amount=50000,
            source="Salary",
        )
        assert result is not None

        total = IncomeRepository.get_total_income()
        assert total == 50000.0


class TestSettingsModel:
    """Test the Settings model and repository."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Set up in-memory database for testing."""
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        
        import database.db as db_module
        self._original_get_engine = db_module.get_engine
        db_module.get_engine = lambda: self.engine
        
        yield
        
        db_module.get_engine = self._original_get_engine

    def test_save_and_retrieve_settings(self):
        """Test saving and retrieving settings."""
        saved = SettingsRepository.save_settings(
            provider="ollama",
            model="llama3",
        )
        assert saved is True

        settings = SettingsRepository.get_settings()
        assert settings is not None
        assert settings.provider == "ollama"
        assert settings.model == "llama3"

    def test_update_settings(self):
        """Test updating existing settings."""
        SettingsRepository.save_settings(provider="ollama", model="llama3")
        SettingsRepository.save_settings(provider="openai", model="gpt-4")

        settings = SettingsRepository.get_settings()
        assert settings.provider == "openai"
        assert settings.model == "gpt-4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])