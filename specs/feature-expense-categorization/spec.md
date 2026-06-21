# Expense Categorization Feature

## Title

Expense categorization using AI-assisted suggestions.

## Overview

Automatically suggest a category when a user adds a new expense, using the expense description and amount.

## Acceptance Criteria

- GIVEN a user enters an expense description
- WHEN the expense is submitted
- THEN the system suggests a category from the configured list
- AND the user can accept or override the suggestion.

## Examples / Scenarios

- Scenario 1: User enters "Uber ride to airport" and the system suggests "Transport".
- Scenario 2: User enters "Grocery store purchase" and the system suggests "Food".

## API / UX Surface

- UI field on expense entry page
- `AIService.categorize_expense(description)` returns a category
- Suggestion displayed before final save

## Notes

This feature links to the AI service provider selector and is intended to reduce manual categorization effort.
