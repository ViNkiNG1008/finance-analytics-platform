import pandas as pd
from datetime import date
from src.analytics.recurring import detect_recurring

def test_detects_monthly_subscription():
    df = pd.DataFrame([
        {"merchant_id": 1, "merchant_name": "Netflix", "category_name": "Entertainment",
         "amount": -499, "txn_date": date(2026, 4, 15)},
        {"merchant_id": 1, "merchant_name": "Netflix", "category_name": "Entertainment",
         "amount": -499, "txn_date": date(2026, 5, 15)},
        {"merchant_id": 1, "merchant_name": "Netflix", "category_name": "Entertainment",
         "amount": -499, "txn_date": date(2026, 6, 15)},
    ])
    result = detect_recurring(df)
    assert len(result) == 1
    assert result[0].frequency == "monthly"
    assert result[0].occurrences == 3

def test_ignores_irregular_spending():
    df = pd.DataFrame([
        {"merchant_id": 2, "merchant_name": "Random Store", "category_name": "Shopping",
         "amount": -200, "txn_date": date(2026, 4, 3)},
        {"merchant_id": 2, "merchant_name": "Random Store", "category_name": "Shopping",
         "amount": -850, "txn_date": date(2026, 5, 22)},
    ])
    result = detect_recurring(df)
    assert len(result) == 0