-- Star schema for the Personal Finance Analytics Platform
-- Fact table: fact_transactions
-- Dimensions: dim_category, dim_merchant, dim_date

CREATE TABLE IF NOT EXISTS dim_category (
    category_id     SERIAL PRIMARY KEY,
    category_name   VARCHAR(50) UNIQUE NOT NULL,
    category_type   VARCHAR(20) NOT NULL CHECK (category_type IN ('Income', 'Expense'))
);

CREATE TABLE IF NOT EXISTS dim_merchant (
    merchant_id     SERIAL PRIMARY KEY,
    merchant_name   VARCHAR(100) UNIQUE NOT NULL,
    default_category_id INTEGER REFERENCES dim_category(category_id)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id         DATE PRIMARY KEY,
    day             SMALLINT NOT NULL,
    month           SMALLINT NOT NULL,
    month_name      VARCHAR(10) NOT NULL,
    quarter         SMALLINT NOT NULL,
    year            SMALLINT NOT NULL,
    day_of_week     VARCHAR(10) NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id      BIGSERIAL PRIMARY KEY,
    date_id              DATE NOT NULL REFERENCES dim_date(date_id),
    merchant_id           INTEGER REFERENCES dim_merchant(merchant_id),
    category_id           INTEGER REFERENCES dim_category(category_id),
    description            TEXT NOT NULL,          -- raw description from statement
    amount                  NUMERIC(12, 2) NOT NULL, -- positive = income, negative = expense
    transaction_type        VARCHAR(20) NOT NULL CHECK (transaction_type IN ('Income', 'Expense')),
    source_file              VARCHAR(255),           -- which uploaded statement this came from
    is_duplicate_flag         BOOLEAN DEFAULT FALSE,
    created_at                TIMESTAMP DEFAULT NOW()
);

-- Helpful indexes for dashboard queries
CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_transactions(date_id);
CREATE INDEX IF NOT EXISTS idx_fact_category ON fact_transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_fact_merchant ON fact_transactions(merchant_id);

-- Seed common categories
INSERT INTO dim_category (category_name, category_type) VALUES
    ('Food & Dining', 'Expense'),
    ('Shopping', 'Expense'),
    ('Transport', 'Expense'),
    ('Bills & Utilities', 'Expense'),
    ('Entertainment', 'Expense'),
    ('Others', 'Expense'),
    ('Income', 'Income')
ON CONFLICT (category_name) DO NOTHING;

-- Seed a few common merchants with default categories (extend in Phase 3)
INSERT INTO dim_merchant (merchant_name, default_category_id)
SELECT 'Swiggy', category_id FROM dim_category WHERE category_name = 'Food & Dining'
ON CONFLICT (merchant_name) DO NOTHING;

INSERT INTO dim_merchant (merchant_name, default_category_id)
SELECT 'Zomato', category_id FROM dim_category WHERE category_name = 'Food & Dining'
ON CONFLICT (merchant_name) DO NOTHING;

INSERT INTO dim_merchant (merchant_name, default_category_id)
SELECT 'Uber', category_id FROM dim_category WHERE category_name = 'Transport'
ON CONFLICT (merchant_name) DO NOTHING;

INSERT INTO dim_merchant (merchant_name, default_category_id)
SELECT 'Amazon', category_id FROM dim_category WHERE category_name = 'Shopping'
ON CONFLICT (merchant_name) DO NOTHING;

INSERT INTO dim_merchant (merchant_name, default_category_id)
SELECT 'Netflix', category_id FROM dim_category WHERE category_name = 'Entertainment'
ON CONFLICT (merchant_name) DO NOTHING;

-- Phase 5: budgets table (one monthly limit per expense category)
CREATE TABLE IF NOT EXISTS budgets (
    budget_id       SERIAL PRIMARY KEY,
    category_id     INTEGER NOT NULL UNIQUE REFERENCES dim_category(category_id),
    monthly_limit   NUMERIC(12, 2) NOT NULL DEFAULT 0
);