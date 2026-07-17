"""
Tests for the ETL pipeline (extract -> transform -> categorize).
Run with: pytest tests/test_etl.py -v
"""
import pandas as pd
from src.etl.transform import clean_transactions
from src.etl.categorize import categorize_transactions


def test_categorize_known_merchant():
    df = pd.DataFrame({
        "merchant": ["Swiggy", "Uber", "Unknown Store"],
        "transaction_type": ["Expense", "Expense", "Expense"],
    })
    result = categorize_transactions(df)
    assert result.loc[0, "category"] == "Food & Dining"
    assert result.loc[1, "category"] == "Transport"
    assert result.loc[2, "category"] == "Others"


def test_income_always_categorized_as_income():
    df = pd.DataFrame({
        "merchant": ["Acme Corp"],
        "transaction_type": ["Income"],
    })
    result = categorize_transactions(df)
    assert result.loc[0, "category"] == "Income"


def test_clean_transactions_dedupes_and_parses():
    raw = pd.DataFrame({
        "Date": ["01-06-2026", "01-06-2026", "02-06-2026"],
        "Description": [
            "UPI-SWIGGY-swiggy@ybl-Order Payment",
            "UPI-SWIGGY-swiggy@ybl-Order Payment",  # exact duplicate
            "SALARY CREDIT-ACME CORP",
        ],
        "Amount": ["-450.00", "-450.00", "50000.00"],
    })
    result = clean_transactions(raw)
    assert len(result) == 2  # duplicate dropped
    assert result.loc[0, "merchant"] == "Swiggy"
    assert result.loc[0, "transaction_type"] == "Expense"
    assert result.loc[1, "transaction_type"] == "Income"
