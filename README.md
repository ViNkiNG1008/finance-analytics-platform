# FinTrack — Personal Finance Analytics Platform

A multi-user, end-to-end pipeline that turns raw bank/UPI statements into an
interactive expense-tracking dashboard, with auto-generated insights,
forecasting, and exportable reports.

Statement (CSV/Excel) → Python ETL → Clean & Categorize → PostgreSQL → Streamlit (Plotly dashboards)

![FinTrack architecture](architecture.png)

## Features

- **Multi-user accounts** — sign up / log in, each user sees only their own transactions and budgets
- **ETL pipeline** — upload a bank/UPI statement (CSV/Excel), automatic column standardization, date parsing, merchant extraction, deduplication on re-upload
- **Rule-based categorization** — merchant → category matching, income handled separately from expenses
- **Interactive dashboard** — income/expense/savings KPIs, category breakdown donut, monthly trend lines, top merchants
- **Budget tracking** — set monthly limits per category, compare budget vs actual with overspend warnings
- **Auto-generated insights** — plain-language observations (e.g. "Shopping is your biggest expense category, 43% of spend")
- **Expense forecasting** — linear-trend forecast for next month's spend, with a confidence level based on available history
- **Recurring payment detection** — flags subscriptions/bills and predicts next expected date
- **Exportable reports** — download any date range as CSV, PDF, or Excel
- **Standalone Power BI file** — same database, DAX measures and visuals, for BI-tool skills independent of the Streamlit app

## Stack

| Layer          | Tool                                    |
|----------------|------------------------------------------|
| Ingestion/ETL  | Python, Pandas                           |
| Database       | PostgreSQL (Neon, star schema)           |
| Auth           | bcrypt + session-based login (no third-party auth provider) |
| Dashboards     | Streamlit + Plotly                       |
| Reports        | ReportLab (PDF), openpyxl (Excel)        |
| Forecasting    | scikit-learn (linear regression)         |
| BI (portfolio) | Power BI (standalone .pbix)              |
| Testing        | pytest                                   |

> Dashboards are built natively in Streamlit with Plotly rather than embedded
> Power BI — this avoids the Power BI Embedded/Azure cost and keeps the whole
> app deployable for free on Streamlit Community Cloud. A separate Power BI
> file against the same database lives in `powerbi/` to demonstrate DAX/BI
> skills independently.

## Schema

Star schema: `fact_transactions` with `dim_date`, `dim_category`, `dim_merchant`
dimension tables, plus `budgets` (one monthly limit per category per user) and
`users` (auth). All transactional data (`fact_transactions`, `budgets`) is
scoped by `user_id`; dimension tables are shared across users.

Sign convention: `amount` is positive for Income, negative for Expense.

## Setup

```bash
# 1. Clone and enter
git clone https://github.com/ViNkiNG1008/finance-analytics-platform.git
cd finance-analytics-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# edit .env with your Postgres/Neon credentials

# 5. Create the database schema
python run_schema.py
python run_migration.py
python run_constraint_fix.py

# 6. Run the app
streamlit run streamlit_app/app.py
```

On first run, go to the **Login** page and use **Sign Up** to create an account.

## Roadmap

- [x] Phase 0: Project scaffolding
- [x] Phase 1: Folder structure, Streamlit shell
- [x] Phase 2: ETL pipeline (extract → clean → categorize → load)
- [x] Phase 4: PostgreSQL star schema
- [x] Phase 5: Streamlit dashboards (Plotly)
- [x] Phase 6: Insights, forecasting, recurring payment detection
- [x] Phase 7: Power BI portfolio file
- [x] Reports: CSV/PDF/Excel export
- [x] Multi-user authentication (signup/login, per-user data scoping)
- [x] Premium dark-theme UI pass
- [ ] Phase 3: ML-based categorization (currently rule-based)
- [ ] Deployment to Streamlit Community Cloud