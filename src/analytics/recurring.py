"""
Detects recurring/subscription-like transactions by grouping on merchant,
checking amount consistency and interval regularity.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean, pstdev
from typing import List, Optional
import pandas as pd

AMOUNT_TOLERANCE_PCT = 0.10      # amounts within ±10% count as "same"
MIN_OCCURRENCES = 3               # need at least 3 hits to call it recurring
INTERVAL_STD_DEV_THRESHOLD = 5    # days; how "regular" the gaps must be

FREQUENCY_BANDS = {
    "weekly": (5, 9),
    "biweekly": (12, 16),
    "monthly": (26, 34),
    "quarterly": (85, 95),
}

@dataclass
class RecurringPayment:
    merchant_id: int
    merchant_name: str
    category_name: str
    avg_amount: float
    frequency: str
    occurrences: int
    last_date: date
    next_expected_date: date
    confidence: str  # "high" / "medium"

def _classify_frequency(avg_interval_days: float) -> Optional[str]:
    for label, (lo, hi) in FREQUENCY_BANDS.items():
        if lo <= avg_interval_days <= hi:
            return label
    return None

def detect_recurring(transactions: pd.DataFrame) -> List[RecurringPayment]:
    """
    transactions: DataFrame with columns
        merchant_id, merchant_name, category_name, amount, txn_date
    Expects only EXPENSE rows (negative amounts) — filter before calling.
    """
    results: List[RecurringPayment] = []

    for merchant_id, grp in transactions.groupby("merchant_id"):
        grp = grp.sort_values("txn_date")
        amounts = grp["amount"].abs().tolist()
        dates = grp["txn_date"].tolist()

        if len(grp) < MIN_OCCURRENCES:
            continue

        # cluster by amount similarity (simple: check against running mean)
        avg_amt = mean(amounts)
        if any(abs(a - avg_amt) / avg_amt > AMOUNT_TOLERANCE_PCT for a in amounts):
            continue

        intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        if not intervals:
            continue

        avg_interval = mean(intervals)
        interval_spread = pstdev(intervals) if len(intervals) > 1 else 0

        if interval_spread > INTERVAL_STD_DEV_THRESHOLD:
            continue

        freq_label = _classify_frequency(avg_interval)
        if freq_label is None:
            continue

        last_date = dates[-1]
        next_expected = last_date + timedelta(days=round(avg_interval))
        confidence = "high" if len(grp) >= 4 and interval_spread <= 3 else "medium"

        results.append(RecurringPayment(
            merchant_id=merchant_id,
            merchant_name=grp["merchant_name"].iloc[0],
            category_name=grp["category_name"].iloc[0],
            avg_amount=round(avg_amt, 2),
            frequency=freq_label,
            occurrences=len(grp),
            last_date=last_date,
            next_expected_date=next_expected,
            confidence=confidence,
        ))

    results.sort(key=lambda r: r.avg_amount, reverse=True)
    return results