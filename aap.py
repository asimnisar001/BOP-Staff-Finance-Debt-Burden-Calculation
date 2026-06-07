"""
BOP Staff Finance – Debt Burden Calculation App
================================================
Streamlit-based web app. Run with:  streamlit run aap.py
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="BOP Staff Finance – Debt Burden Calculator",
    page_icon="🏦",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&family=Source+Code+Pro&display=swap');

html, body, [class*="css"] { font-family: 'EB Garamond', serif; }

.main { background-color: #0d1b36; }

h1, h2, h3 { color: #f0c040 !important; }

.stApp { background-color: #0d1b36; color: #c8d8f0; }

div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label { color: #c8d8f0 !important; font-size: 0.97rem; }

div[data-testid="stNumberInput"] input {
    background-color: #0a1428 !important;
    color: #f0e68c !important;
    border: 1px solid #2a4070 !important;
    border-radius: 4px;
    font-family: 'Source Code Pro', monospace;
}

.result-box {
    background: #060f22;
    border: 1px solid #243b6e;
    border-radius: 8px;
    padding: 18px 22px;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.93rem;
    color: #c8d8f0;
    margin-top: 8px;
}
.res-header  { color: #f0c040; font-weight: bold; margin-top: 14px; }
.res-value   { color: #44ffaa; font-weight: bold; }
.res-alert   { color: #ff6b6b; font-weight: bold; }
.res-cushion { color: #ffd700; }
.res-sep     { color: #334e88; }
.res-label   { color: #c8d8f0; }

.petrol-banner {
    background: #162040;
    border-radius: 6px;
    padding: 8px 16px;
    color: #44ffaa;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.95rem;
    margin-bottom: 12px;
}

.stButton > button {
    background-color: #1e5aa8;
    color: white;
    border: none;
    border-radius: 6px;
    font-family: 'EB Garamond', serif;
    font-size: 1.05rem;
    padding: 0.45rem 2rem;
}
.stButton > button:hover { background-color: #2970cc; }

section[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Petrol price scraper ──────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_petrol_price() -> float:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://propakistani.pk/petrol-price-in-pakistan/"
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        for row in soup.find_all("tr"):
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            for i, cell in enumerate(cells):
                if "petrol" in cell.lower() and i + 1 < len(cells):
                    price_text = cells[i + 1].replace(",", "").replace("Rs", "").replace("PKR", "").strip()
                    price = float("".join(c for c in price_text if c.isdigit() or c == "."))
                    if 100 < price < 1000:
                        return price
    except Exception:
        pass
    return 262.48   # fallback – latest known OGRA rate


# ── Header ────────────────────────────────────────────────────────────
st.markdown("## 🏦 Bank of Punjab")
st.markdown("### Staff Finance · Debt Burden Calculator")
st.markdown("---")

# ── Live petrol price ─────────────────────────────────────────────────
petrol_price = fetch_petrol_price()
st.markdown(
    f'<div class="petrol-banner">⛽ &nbsp; Current Petrol Price (Pakistan): '
    f'<strong>PKR {petrol_price:,.2f} / litre</strong></div>',
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════
#  INPUT SECTIONS
# ═══════════════════════════════════════════════════════════════════════

# ── 1. Monthly Salary ─────────────────────────────────────────────────
st.markdown("#### 💼 Monthly Salary")
col1, col2 = st.columns(2)
with col1:
    basic        = st.number_input("Basic Salary (PKR)",          min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    house_rent   = st.number_input("House Rent Allowance (PKR)",  min_value=0.0, value=0.0,      step=500.0,  format="%.2f")
with col2:
    medical      = st.number_input("Medical Allowance (PKR)",     min_value=0.0, value=0.0,      step=500.0,  format="%.2f")
    other_allow  = st.number_input("Other Allowances (PKR)",      min_value=0.0, value=0.0,      step=500.0,  format="%.2f")

monthly_salary = basic + medical + house_rent + other_allow

# ── 2. Monthly Perks ──────────────────────────────────────────────────
st.markdown("#### ⛽ Monthly Perks")
col3, col4 = st.columns(2)
with col3:
    petrol_qty   = st.number_input("Petrol Quantity (litres/month)", min_value=0.0, value=100.0, step=5.0,   format="%.1f")
    servant_sal  = st.number_input("Servant Salary (PKR)",           min_value=0.0, value=0.0,   step=500.0, format="%.2f")
with col4:
    driver_sal   = st.number_input("Driver Salary (PKR)",            min_value=0.0, value=0.0,   step=500.0, format="%.2f")
    mobile_cost  = st.number_input("Mobile Cost (PKR)",              min_value=0.0, value=0.0,   step=100.0, format="%.2f")

petrol_cost          = petrol_qty * petrol_price
total_monthly_perks  = petrol_cost + driver_sal + servant_sal + mobile_cost

# ── 3. Existing Loans ─────────────────────────────────────────────────
st.markdown("#### 🏦 Existing Loan Deductions (Monthly Instalments)")
col5, col6, col7 = st.columns(3)
with col5:
    car_inst      = st.number_input("Car Loan (PKR)",      min_value=0.0, value=0.0, step=500.0, format="%.2f")
with col6:
    house_inst    = st.number_input("House Loan (PKR)",    min_value=0.0, value=0.0, step=500.0, format="%.2f")
with col7:
    personal_inst = st.number_input("Personal Loan (PKR)", min_value=0.0, value=0.0, step=500.0, format="%.2f")

total_existing = car_inst + house_inst + personal_inst

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
#  CALCULATE BUTTON
# ═══════════════════════════════════════════════════════════════════════
if st.button("⚙️  Calculate Debt Burden"):

    # ── Derived values ────────────────────────────────────────────────
    festival_bonus         = basic * 2
    festival_bonus_monthly = festival_bonus / 12

    annual_salary   = monthly_salary * 12
    annual_perks    = total_monthly_perks * 12
    annual_festival = festival_bonus          # paid once per year

    total_annual_salary = annual_salary + annual_perks + annual_festival
    effective_monthly   = total_annual_salary / 12
    total_csr           = total_annual_salary / 2
    monthly_csr         = total_csr / 12

    debt_burden = monthly_csr - total_existing

    house_cushion = basic * 150
    car_cushion   = basic * 50
    gp_cushion    = basic * 8

    # ── Helper to format PKR ──────────────────────────────────────────
    def pkr(v):
        return f"PKR {v:>16,.2f}"

    def row_html(label, value, cls="res-value"):
        return (
            f'<div style="display:flex;justify-content:space-between;padding:2px 0">'
            f'<span class="res-label">{label}</span>'
            f'<span class="{cls}">{pkr(value)}</span>'
            f'</div>'
        )

    SEP = '<div class="res-sep" style="margin:4px 0">──────────────────────────────────────────────────────────</div>'

    def section(title):
        return f'<div class="res-header">● {title}</div>{SEP}'

    html = '<div class="result-box">'

    # Monthly Salary
    html += section("Monthly Salary Breakdown")
    html += row_html("Basic Salary",               basic)
    html += row_html("Medical Allowance",           medical)
    html += row_html("House Rent Allowance",        house_rent)
    html += row_html("Other Allowances",            other_allow)
    html += row_html("Total Monthly Salary",        monthly_salary)

    # Perks
    html += section("Monthly Perks")
    html += (f'<div style="display:flex;justify-content:space-between;padding:2px 0">'
             f'<span class="res-label">Petrol Rate</span>'
             f'<span class="res-value">PKR {petrol_price:>10,.2f} / litre</span></div>')
    html += row_html(f"Petrol Cost  ({petrol_qty:.0f} L × {petrol_price:.2f})", petrol_cost)
    html += row_html("Driver Salary",               driver_sal)
    html += row_html("Servant Salary",              servant_sal)
    html += row_html("Mobile Cost",                 mobile_cost)
    html += row_html("Total Monthly Perks",         total_monthly_perks)

    # Festival Bonus
    html += section("Festival Bonus")
    html += row_html("Festival Bonus  (Basic × 2)",     festival_bonus)
    html += row_html("Monthly Amortised  (÷ 12)",       festival_bonus_monthly)

    # Annual
    html += section("Annual Salary Calculation")
    html += row_html("Annual Salary  (monthly × 12)",   annual_salary)
    html += row_html("Annual Perks   (perks × 12)",     annual_perks)
    html += row_html("Annual Festival Bonus",           annual_festival)
    html += row_html("Total Annual Salary",             total_annual_salary)

    # CSR
    html += section("Current Service Ratio (CSR)")
    html += row_html("Effective Monthly  (Annual ÷ 12)", effective_monthly)
    html += row_html("Total CSR  (Annual ÷ 2)",          total_csr)
    html += row_html("Monthly CSR  (CSR ÷ 12)",          monthly_csr)

    # Existing deductions
    html += section("Existing Loan Deductions (Monthly)")
    html += row_html("Car Loan Instalment",          car_inst)
    html += row_html("House Loan Instalment",        house_inst)
    html += row_html("Personal Loan Instalment",     personal_inst)
    html += row_html("Total Existing Deductions",    total_existing)

    # Debt Burden
    html += section("Debt Burden")
    if debt_burden >= 0:
        html += row_html("Debt Burden  (Monthly CSR – Deductions)", debt_burden, "res-value")
    else:
        html += row_html("Debt Burden  ⚠ NEGATIVE – Over-Committed", debt_burden, "res-alert")
        html += '<div class="res-alert" style="margin-top:6px">⚠  Staff member has exceeded repayment capacity.</div>'

    # Loan Cushions
    html += section("Maximum Eligible Loan Amounts (Cushions)")
    html += row_html("House Loan  (150 × Basic Salary)", house_cushion, "res-cushion")
    html += row_html("Car Loan    ( 50 × Basic Salary)", car_cushion,   "res-cushion")
    html += row_html("General Purpose  (8 × Basic Salary)", gp_cushion, "res-cushion")

    html += SEP + "</div>"

    st.markdown(html, unsafe_allow_html=True)

else:
    st.info("Fill in the fields above and click **Calculate Debt Burden** to see results.")

st.markdown("---")
st.caption("Bank of Punjab · Staff Finance Division · Debt Burden Calculator")
