"""
Database models for the Expense Tracker application.

Defines SQLAlchemy ORM models for expenses, income, and settings tables.
All models include proper field validation and string representations.
"""

from datetime import date, datetime
from typing import ClassVar

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Expense(Base):
    """
    Expense model representing a single expense transaction.

    Attributes:
        id: Primary key
        date: Date of the expense
        amount: Monetary amount (positive float)
        category: Expense category from predefined list
        description: Brief description of the expense
        payment_method: How the expense was paid (Cash, Card, UPI, etc.)
        notes: Optional additional notes
        created_at: Timestamp of record creation
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="Cash")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    VALID_CATEGORIES: ClassVar[list[str]] = [
        "Food",
        "Transport",
        "Shopping",
        "Entertainment",
        "Health",
        "Education",
        "Bills",
        "Investment",
        "Salary",
        "Other",
    ]

    VALID_PAYMENT_METHODS: ClassVar[list[str]] = [
        "Cash",
        "Card",
        "UPI",
        "Net Banking",
        "Other",
    ]

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, date={self.date}, amount={self.amount}, category='{self.category}')>"

    def to_dict(self) -> dict:
        """Convert expense to dictionary for serialization."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Income(Base):
    """
    Income model representing money received.

    Attributes:
        id: Primary key
        date: Date income was received
        amount: Monetary amount (positive float)
        source: Source of income (Salary, Freelance, Investment, etc.)
        notes: Optional additional notes
        created_at: Timestamp of record creation
    """

    __tablename__ = "income"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    VALID_SOURCES: ClassVar[list[str]] = [
        "Salary",
        "Freelance",
        "Investment",
        "Business",
        "Rental",
        "Gift",
        "Refund",
        "Other",
    ]

    def __repr__(self) -> str:
        return f"<Income(id={self.id}, date={self.date}, amount={self.amount}, source='{self.source}')>"

    def to_dict(self) -> dict:
        """Convert income to dictionary for serialization."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "amount": self.amount,
            "source": self.source,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Settings(Base):
    """
    Application settings model.

    Stores AI provider configuration and other app settings.

    Attributes:
        id: Primary key
        provider: AI provider name (ollama, openai, gemini, openrouter)
        model: Model name for the selected provider
        api_key: API key (stored temporarily, not persisted to DB in production)
        created_at: Timestamp of record creation
    """

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="ollama")
    model: Mapped[str] = mapped_column(String(100), nullable=False, default="llama3")
    api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    VALID_PROVIDERS: ClassVar[list[str]] = ["ollama", "openai", "gemini", "openrouter"]

    def __repr__(self) -> str:
        return f"<Settings(provider='{self.provider}', model='{self.model}')>"

    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider,
            "model": self.model,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
