"""
Shared premium theming: custom CSS injection + branded sidebar header.
Matches the FinTrack ledger design system: navy surfaces, gold accent,
teal/coral semantics for income/expense, Space Grotesk + IBM Plex Mono.
Call apply_theme() right after st.set_page_config() on every page.
"""
import streamlit as st

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ---- Base surfaces ---- */
.stApp {
    background-color: #111820;
}
[data-testid="stHeader"] {
    background-color: transparent;
}
[data-testid="stAppViewBlockContainer"] {
    padding-top: 2.5rem;
    max-width: 1200px;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background-color: #111820;
    border-right: 1px solid #232D38;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}
[data-testid="stSidebarNav"] li a {
    border-radius: 6px;
    padding: 7px 12px;
    margin: 1px 8px;
    font-weight: 500;
    font-size: 0.875rem;
    color: #7C8894 !important;
    transition: all 0.12s ease;
}
[data-testid="stSidebarNav"] li a:hover {
    background-color: #171F28;
    color: #EDF1F5 !important;
}
[data-testid="stSidebarNav"] li a[aria-current="page"] {
    background-color: rgba(201, 162, 39, 0.10);
    color: #C9A227 !important;
    font-weight: 600;
    border-left: 2px solid #C9A227;
}

/* ---- Headings ---- */
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
}
h1 {
    font-weight: 600 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.01em;
    color: #EDF1F5;
    margin-bottom: 0.2rem;
}
h2 { font-weight: 500 !important; font-size: 1.1rem !important; color: #EDF1F5; }
h3 { font-weight: 500 !important; font-size: 1rem !important; color: #EDF1F5; }
[data-testid="stCaptionContainer"] {
    color: #7C8894 !important;
    font-size: 0.85rem;
}

/* ---- Native st.metric (kept as fallback where render_metric isn't used) ---- */
[data-testid="stMetric"] {
    background: #171F28;
    border-left: 3px solid #C9A227;
    border-radius: 0 10px 10px 0;
    padding: 14px 16px;
    min-height: 88px;
}
[data-testid="stMetricLabel"] {
    color: #7C8894;
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricValue"] {
    color: #EDF1F5 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 1.3rem !important;
}

/* ---- Buttons ---- */
.stButton button, .stDownloadButton button {
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.875rem;
    border: 1px solid #232D38;
    background: #171F28;
    color: #EDF1F5;
    transition: all 0.12s ease;
    padding: 0.45rem 1rem;
}
.stButton button:hover, .stDownloadButton button:hover {
    border-color: #C9A227;
    color: #C9A227;
}
.stButton button[kind="primary"] {
    background: #C9A227;
    color: #1A1400;
    border: none;
}
.stButton button[kind="primary"]:hover {
    background: #DDB534;
    color: #1A1400;
}

/* ---- Inputs ---- */
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox [data-baseweb="select"] {
    background-color: #171F28 !important;
    border: 1px solid #232D38 !important;
    border-radius: 8px !important;
    color: #EDF1F5 !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #C9A227 !important;
    box-shadow: none !important;
}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #232D38;
}
.stTabs [data-baseweb="tab"] {
    color: #7C8894;
    font-weight: 500;
    font-size: 0.875rem;
    padding: 8px 4px;
}
.stTabs [aria-selected="true"] {
    color: #C9A227 !important;
    border-bottom-color: #C9A227 !important;
}

/* ---- Forms / cards ---- */
[data-testid="stForm"] {
    background: #171F28;
    border: 1px solid #232D38;
    border-radius: 12px;
    padding: 20px;
}

/* ---- Dataframes ---- */
[data-testid="stDataFrame"] {
    border: 1px solid #232D38;
    border-radius: 10px;
    overflow: hidden;
}

/* ---- Alerts ---- */
[data-testid="stAlertContainer"] {
    border-radius: 10px;
    border: 1px solid;
    font-size: 0.875rem;
}

/* ---- Divider ---- */
hr {
    border-color: #232D38 !important;
    margin: 1.5rem 0 !important;
}

#MainMenu, footer {visibility: hidden;}
</style>
"""

BRAND_HTML = """
<div style="display:flex; align-items:center; gap:10px; padding: 4px 4px 22px 4px;">
    <div style="width:30px; height:30px; border-radius:8px;
                background:#C9A227;
                display:flex; align-items:center; justify-content:center;
                font-family:'Space Grotesk', sans-serif; font-size:15px; font-weight:600; color:#1A1400;">₹</div>
    <div>
        <div style="font-family:'Space Grotesk', sans-serif; font-size:0.95rem; font-weight:600; color:#EDF1F5; line-height:1.1;">FinTrack</div>
        <div style="font-size:0.65rem; color:#7C8894; letter-spacing:0.05em;">PERSONAL FINANCE</div>
    </div>
</div>
"""


def apply_theme() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_sidebar_brand() -> None:
    with st.sidebar:
        st.markdown(BRAND_HTML, unsafe_allow_html=True)
        if st.session_state.get("authenticated"):
            name = st.session_state.get("name", "")
            username = st.session_state.get("username", "")
            st.markdown(
                f"""
                <div style="margin-top:16px; padding:10px 12px; background:#171F28;
                            border:1px solid #232D38; border-radius:8px; font-size:0.78rem;">
                    <div style="color:#EDF1F5; font-weight:500;">{name}</div>
                    <div style="color:#7C8894;">@{username}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------
# Ledger-style KPI cards (colored left accent), matching the mockups
# ---------------------------------------------------------------------
METRIC_COLORS = {
    "income": "#2FBF8F",
    "expense": "#E8734D",
    "savings": "#C9A227",
    "rate": "#4C8DFF",
    "neutral": "#7C8894",
}


def render_metric(label: str, value: str, kind: str = "neutral") -> None:
    accent = METRIC_COLORS.get(kind, "#7C8894")
    st.markdown(
        f"""
        <div style="background:#171F28; border-left:3px solid {accent};
                    border-radius:0 10px 10px 0; padding:14px 16px; min-height:88px;">
            <div style="color:#7C8894; font-size:0.68rem; font-weight:600; text-transform:uppercase;
                        letter-spacing:0.06em; margin-bottom:6px;">{label}</div>
            <div style="color:#EDF1F5; font-family:'IBM Plex Mono', monospace; font-weight:500;
                        font-size:1.3rem;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Category pill colors, matching the transactions mockup exactly
# ---------------------------------------------------------------------
CATEGORY_STYLES = {
    "Food & Dining":     {"bg": "#2A2114", "text": "#E8A33D"},
    "Bills & Utilities": {"bg": "#132A3D", "text": "#6BA6FF"},
    "Shopping":          {"bg": "#2A2114", "text": "#C9A227"},
    "Income":            {"bg": "#12241C", "text": "#2FBF8F"},
    "Transport":         {"bg": "#12241C", "text": "#2FBF8F"},
    "Entertainment":     {"bg": "#201A2E", "text": "#8B5CF6"},
    "Others":            {"bg": "#1D2530", "text": "#7C8894"},
}

# Plotly-friendly flat map (category_name -> hex) for donut/bar charts
CATEGORY_HEX = {k: v["text"] for k, v in CATEGORY_STYLES.items()}


def style_category(val):
    """Use with df.style.map(style_category, subset=['Category']) in st.dataframe."""
    s = CATEGORY_STYLES.get(val, CATEGORY_STYLES["Others"])
    return f"background-color: {s['bg']}; color: {s['text']}; border-radius: 10px;"


# ---------------------------------------------------------------------
# Budget vs actual progress bars — teal under, gold near limit, coral over
# ---------------------------------------------------------------------
def render_budget_bar(category_name: str, actual_spent: float, monthly_limit: float) -> None:
    pct_raw = (actual_spent / monthly_limit * 100) if monthly_limit > 0 else 0
    pct = min(pct_raw, 100)
    if pct_raw >= 100:
        bar_color = "#E8734D"
    elif pct_raw >= 60:
        bar_color = "#C9A227"
    else:
        bar_color = "#2FBF8F"

    st.markdown(
        f"""
        <div style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:5px;">
                <span>{category_name}</span>
                <span style="color:#7C8894; font-family:'IBM Plex Mono', monospace;">₹{actual_spent:,.0f} / ₹{monthly_limit:,.0f}</span>
            </div>
            <div style="height:6px; background:#232D38; border-radius:3px; overflow:hidden;">
                <div style="width:{pct}%; height:100%; background:{bar_color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Observation feed row for the Insights page
# ---------------------------------------------------------------------
def render_observation(text: str, kind: str = "neutral") -> None:
    accent = METRIC_COLORS.get(kind, "#7C8894")
    st.markdown(
        f"""
        <div style="background:#171F28; border-radius:10px; padding:11px 14px; margin-bottom:8px;
                    display:flex; gap:10px; align-items:flex-start;">
            <div style="width:6px; height:6px; border-radius:50%; background:{accent}; margin-top:7px; flex-shrink:0;"></div>
            <span style="font-size:0.85rem; color:#EDF1F5;">{text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Shared Plotly styling
# ---------------------------------------------------------------------
CHART_COLORS = ["#C9A227", "#4C8DFF", "#E8734D", "#7C8894", "#8B5CF6", "#2FBF8F"]


def style_chart(fig, height=320):
    fig.update_layout(
        height=height,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#EDF1F5", size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        colorway=CHART_COLORS,
    )
    fig.update_xaxes(gridcolor="#232D38", zerolinecolor="#232D38")
    fig.update_yaxes(gridcolor="#232D38", zerolinecolor="#232D38")
    return fig


def empty_state(message: str, icon: str = "—") -> None:
    st.markdown(
        f"""
        <div style="text-align:center; padding: 32px 16px; background:#171F28;
                    border:1px dashed #232D38; border-radius:10px; color:#7C8894;">
            <div style="font-size:1.3rem; margin-bottom:6px;">{icon}</div>
            <div style="font-size:0.85rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_inr(amount: float) -> str:
    abs_amt = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_amt >= 1_00_00_000:
        return f"{sign}₹{abs_amt / 1_00_00_000:.2f}Cr"
    elif abs_amt >= 1_00_000:
        return f"{sign}₹{abs_amt / 1_00_000:.2f}L"
    else:
        return f"{sign}₹{abs_amt:,.0f}"