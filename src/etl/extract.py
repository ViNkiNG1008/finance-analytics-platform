"""
Extract: read an uploaded statement (CSV or Excel) into a raw DataFrame.
Phase 2 will implement the actual parsing logic here.
"""
import pandas as pd
from pathlib import Path


def extract_statement(file_path: str | Path) -> pd.DataFrame:
    """
    Read a bank/UPI statement file and return a raw DataFrame.

    Expected input columns (varies by bank, standardized in transform.py):
        Date, Description, Amount  (at minimum)

    Args:
        file_path: path to the uploaded .csv or .xlsx file

    Returns:
        Raw, unmodified DataFrame straight from the file.
    """
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    elif file_path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    return df
