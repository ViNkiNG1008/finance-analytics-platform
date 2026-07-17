"""
Auto-categorization: assign a category to each transaction.

Income transactions always map to the 'Income' category.
Expense transactions are matched against a merchant keyword rule set,
falling back to 'Others' when nothing matches.

Extend MERCHANT_CATEGORY_MAP as you see new real merchant strings —
this is the first thing worth tuning once you upload your own statement.
"""
import pandas as pd

MERCHANT_CATEGORY_MAP = {
    # Food & Dining
    "swiggy": "Food & Dining",
    "zomato": "Food & Dining",
    "dominos": "Food & Dining",
    "mcdonald": "Food & Dining",
    "starbucks": "Food & Dining",
    # Transport
    "uber": "Transport",
    "ola": "Transport",
    "rapido": "Transport",
    "irctc": "Transport",
    "petrol": "Transport",
    # Shopping
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "myntra": "Shopping",
    "ajio": "Shopping",
    "blinkit": "Shopping",
    "bigbasket": "Shopping",
    "zepto": "Shopping",
    # Entertainment
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "prime video": "Entertainment",
    "hotstar": "Entertainment",
    "bookmyshow": "Entertainment",
    # Bills & Utilities
    "airtel": "Bills & Utilities",
    "jio": "Bills & Utilities",
    "vodafone": "Bills & Utilities",
    "vi ": "Bills & Utilities",
    "electricity": "Bills & Utilities",
    "mseb": "Bills & Utilities",
    "water bill": "Bills & Utilities",
    "municipal": "Bills & Utilities",
    "broadband": "Bills & Utilities",
    "wifi": "Bills & Utilities",
}


def _match_category(merchant: str) -> str:
    merchant_lower = str(merchant).lower()
    for keyword, category in MERCHANT_CATEGORY_MAP.items():
        if keyword in merchant_lower:
            return category
    return "Others"


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a 'category' column to the DataFrame.

    Requires columns: 'merchant', 'transaction_type'
    ('transaction_type' should be 'Income' or 'Expense' — see transform.py)
    """
    df = df.copy()

    def categorize_row(row):
        if row.get("transaction_type") == "Income":
            return "Income"
        return _match_category(row["merchant"])

    df["category"] = df.apply(categorize_row, axis=1)
    return df
