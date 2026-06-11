"""
Sample data generator for the Expense Tracker application.

Provides sample expenses and income records for testing and demonstration.
Run this script to populate the database with realistic sample data.
"""

import logging
from datetime import date, timedelta
from random import choice, randint, uniform, seed

from database.db import init_db
from database.repository import ExpenseRepository, IncomeRepository
from database.models import Expense, Income

logger = logging.getLogger(__name__)

# Sample expense descriptions by category
SAMPLE_EXPENSES = {
    "Food": [
        "Swiggy Order - Pizza",
        "Zomato Delivery - Chinese",
        "Lunch at Office Cafeteria",
        "Dinner at Italian Restaurant",
        "Grocery Shopping - Big Bazaar",
        "Morning Coffee - Starbucks",
        "Weekly Groceries - Reliance Fresh",
        "Dominos Pizza Delivery",
        "Dinner at Local Restaurant",
        "Ice Cream at Corner Shop",
    ],
    "Transport": [
        "Uber Ride to Office",
        "Ola Ride - Airport Drop",
        "Metro Card Recharge",
        "Bus Pass - Monthly",
        "Fuel - Indian Oil Petrol",
        "Auto Rickshaw - Local",
        "Cab to Railway Station",
        "Parking Fee - Mall",
        "Toll Tax - Highway",
        "Bike Service - Regular",
    ],
    "Shopping": [
        "Amazon - Electronics",
        "Flipkart - Clothing",
        "Myntra - Summer Collection",
        "DMart - Monthly Shopping",
        "Lifestyle Store - Shoes",
        "Titan Watch Purchase",
        "Mobile Accessories",
        "Home Decor Items",
        "Kitchen Appliances",
        "Christmas Gift Shopping",
    ],
    "Entertainment": [
        "Movie Tickets - PVR",
        "Netflix Monthly Subscription",
        "Spotify Premium",
        "Concert Tickets",
        "Amazon Prime Renewal",
        "Game Purchase - Steam",
        "Bowling with Friends",
        "Weekend Trip - Local",
        "Book Purchase",
        "Zoo Entry Tickets",
    ],
    "Health": [
        "Doctor Consultation",
        "Pharmacy - Medicines",
        "Health Supplements",
        "Gym Membership",
        "Yoga Class Fee",
        "Blood Test - Lab",
        "Dental Checkup",
        "Eye Checkup - Specs",
        "Health Insurance Premium",
        "Ayurvedic Treatment",
    ],
    "Education": [
        "Online Course - Udemy",
        "Coursera Subscription",
        "Books - Amazon",
        "Workshop Registration",
        "Certification Exam Fee",
        "Language Class Fee",
        "Skill Development Course",
        "Study Materials",
        "Tuition Fee",
        "Conference Registration",
    ],
    "Bills": [
        "Electricity Bill - Monthly",
        "Water Bill - Municipal",
        "Gas Bill - Monthly",
        "Internet Bill - Airtel",
        "Mobile Recharge - Jio",
        "Broadband Bill",
        "DTH Recharge - Tata Sky",
        "Maintenance Charges",
        "Property Tax",
        "Credit Card Bill",
    ],
    "Investment": [
        "Mutual Fund - SIP",
        "Stock Purchase - NSE",
        "Fixed Deposit - Monthly",
        "PPF Contribution",
        "NPS Investment",
        "Gold Purchase - Digital",
        "Treasury Bills",
        "Bond Investment",
        "ETF Purchase",
        "SGB Investment",
    ],
    "Other": [
        "Donation - Charity",
        "Birthday Gift",
        "Wedding Gift",
        "Pet Supplies",
        "Home Repair",
        "Car Wash",
        "Laundry Service",
        "ATM Charges",
        "Subscription - Other",
        "Miscellaneous",
    ],
}

SAMPLE_INCOME = [
    {"source": "Salary", "min": 40000, "max": 80000},
    {"source": "Freelance", "min": 5000, "max": 25000},
    {"source": "Investment", "min": 1000, "max": 10000},
    {"source": "Business", "min": 10000, "max": 50000},
    {"source": "Rental", "min": 5000, "max": 15000},
    {"source": "Gift", "min": 500, "max": 5000},
    {"source": "Refund", "min": 200, "max": 3000},
    {"source": "Other", "min": 100, "max": 2000},
]

PAYMENT_METHODS = ["Cash", "Card", "UPI", "Net Banking", "Other"]


def generate_sample_data(num_expenses: int = 100, num_income: int = 12):
    """
    Generate and insert sample data into the database.
    
    Args:
        num_expenses: Number of sample expense records to create
        num_income: Number of sample income records to create
        
    Returns:
        Tuple of (expenses_created, income_created)
    """
    seed(42)  # Reproducible results
    init_db()

    today = date.today()
    expenses_created = 0
    income_created = 0

    logger.info("Generating %d sample expenses...", num_expenses)

    for i in range(num_expenses):
        # Random date within the last 6 months
        days_ago = randint(0, 180)
        expense_date = today - timedelta(days=days_ago)

        # Pick a random category and description
        category = choice(list(SAMPLE_EXPENSES.keys()))
        description = choice(SAMPLE_EXPENSES[category])

        # Random amount based on category
        if category == "Food":
            amount = round(uniform(50, 2000), 2)
        elif category == "Transport":
            amount = round(uniform(20, 2000), 2)
        elif category == "Shopping":
            amount = round(uniform(200, 15000), 2)
        elif category == "Entertainment":
            amount = round(uniform(100, 5000), 2)
        elif category == "Health":
            amount = round(uniform(100, 5000), 2)
        elif category == "Education":
            amount = round(uniform(200, 10000), 2)
        elif category == "Bills":
            amount = round(uniform(200, 8000), 2)
        elif category == "Investment":
            amount = round(uniform(500, 50000), 2)
        else:
            amount = round(uniform(50, 5000), 2)

        payment = choice(PAYMENT_METHODS)

        result = ExpenseRepository.add_expense(
            expense_date=expense_date,
            amount=amount,
            category=category,
            description=description,
            payment_method=payment,
            notes=f"Sample expense #{i + 1}",
        )
        if result:
            expenses_created += 1

    logger.info("Generating %d sample income records...", num_income)

    for i in range(num_income):
        # Monthly income for the past year
        month_offset = i
        year = today.year - ((12 - month_offset) // 12) if month_offset >= today.month else today.year
        month = ((today.month - month_offset - 1) % 12) + 1

        try:
            income_date = date(year, month, 1)
        except ValueError:
            income_date = date(year, month, 28)

        income_info = choice(SAMPLE_INCOME)
        amount = round(uniform(income_info["min"], income_info["max"]), 2)

        result = IncomeRepository.add_income(
            income_date=income_date,
            amount=amount,
            source=income_info["source"],
            notes=f"Sample income #{i + 1}",
        )
        if result:
            income_created += 1

    logger.info(
        "Sample data generated: %d expenses, %d income records",
        expenses_created,
        income_created,
    )

    return expenses_created, income_created


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Generating sample data for AI Expense Tracker...")
    expenses, income = generate_sample_data()
    print(f"✅ Created {expenses} expenses and {income} income records!")