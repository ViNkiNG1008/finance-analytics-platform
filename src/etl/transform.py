"""
Transform: clean and standardize a raw statement DataFrame into the
internal schema used by categorize.py and load.py:

    ['date', 'description', 'merchant', 'amount', 'transaction_type']

Handles the messiness typical of Indian bank/UPI exports:
- Multiple date formats
- Amount sometimes has commas / currency symbols
- Merchant name buried inside a long UPI description string
- Duplicate rows (double-charged, or re-exported statements)
"""
import re
import pandas as pd

# Common column name variants seen across different bank export formats.
COLUMN_ALIASES = {
    "date": ["date", "transaction date", "txn date", "value date"],
    "description": ["description", "narration", "particulars", "details"],
    "amount": ["amount", "amount (inr)", "transaction amount", "debit/credit"],
}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename whatever columns exist to our internal names: date, description, amount."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    rename_map = {}
    for internal_name, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if col in aliases:
                rename_map[col] = internal_name
                break

    df = df.rename(columns=rename_map)

    missing = {"date", "description", "amount"} - set(df.columns)
    if missing:
        raise ValueError(f"Statement is missing required column(s): {missing}")

    return df[["date", "description", "amount"]]


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates robustly, trying day-first (common in Indian statements) first."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    bad_rows = df["date"].isna().sum()
    if bad_rows:
        df = df.dropna(subset=["date"])
    return df


def _clean_amount(df: pd.DataFrame) -> pd.DataFrame:
    """Strip currency symbols/commas and coerce to float."""
    df = df.copy()
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(r"[₹,]", "", regex=True)
        .str.replace(r"\s+", "", regex=True)
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    return df


def _extract_merchant(description: str) -> str:
    """
    Pull a clean merchant name out of a raw statement description.

    Handles patterns like:
        "UPI-SWIGGY-swiggy@ybl-Order Payment"  -> "Swiggy"
        "NEFT-AIRTEL PAYMENTS BANK-Mobile Recharge" -> "Airtel Payments Bank"
        "SALARY CREDIT JUNE-ACME CORP" -> "Salary Credit June"
    """
    text = str(description).strip()

    # UPI/NEFT-style: prefix-MERCHANT-vpa@handle-note  -> take the 2nd hyphen-segment
    parts = [p.strip() for p in text.split("-") if p.strip()]
    if len(parts) >= 2 and parts[0].upper() in ("UPI", "NEFT", "IMPS", "RTGS"):
        merchant = parts[1]
    elif len(parts) >= 1:
        merchant = parts[0]
    else:
        merchant = text

    # Drop any leftover VPA-looking token (contains '@')
    merchant = re.sub(r"\S+@\S+", "", merchant).strip()

    # Title-case for consistent display ("SWIGGY" -> "Swiggy")
    merchant = merchant.title()

    return merchant if merchant else "Unknown"


def _add_merchant_and_type(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["merchant"] = df["description"].apply(_extract_merchant)
    df["transaction_type"] = df["amount"].apply(lambda a: "Income" if a > 0 else "Expense")
    return df


def _deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate transactions (same date, description, amount)."""
    return df.drop_duplicates(subset=["date", "description", "amount"], keep="first")


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize a raw statement DataFrame into the internal schema:
    ['date', 'description', 'merchant', 'amount', 'transaction_type']
    """
    df = _standardize_columns(df)
    df = _parse_dates(df)
    df = _clean_amount(df)
    df = _add_merchant_and_type(df)
    df = _deduplicate(df)
    df = df.sort_values("date").reset_index(drop=True)
    return df
