"""
BOP Staff Finance – Debt Burden Calculation App
================================================
Pure Streamlit app – no desktop dependencies.
Deploy on Streamlit Cloud:  streamlit run aap.py
"""

import streamlit as st
import requests

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="BOP Staff Finance – Debt Burden Calculator",
    page_icon="🏦",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&family=Source+Code+Pro&display=swap');

html, body, [class*="css"] { font-family: 'EB Garamond', serif; }
.stApp { background-color: #0d1b36; color: #c8d8f0; }
h1, h2, h3, h4 { color: #f0c040 !important; }

div[data-testid="stNumberInput"] label { color: #c8d8f0 !important; font-size: 0.97rem; }
div[data-testid="stNumberInput"] input {
    background-color: #0a1428 !important;
    color: #f0e68c !important;
    border: 1px solid #2a4070 !important;
    border-radius: 4px;
    font-family: 'Source Code Pro', monospace;
}

.petrol-banner {
    background: #162040; border-radius: 6px;
    padding: 8px 16px; color: #44ffaa;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.95rem; margin-bottom: 12px;
}
.result-box {
    background: #060f22; border: 1px solid #243b6e;
    border-radius: 8px; padding: 18px 22px;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.93rem; color: #c8d8f0; margin-top: 8px;
}
.res-header  { color: #f0c040; font-weight: bold; margin-top: 14px; }
.res-value   { color: #44ffaa; font-weight: bold; }
.res-alert   { color: #ff6b6b; font-weight: bold; }
.res-cushion { color: #ffd700; }
.res-sep     { color: #334e88; }
.res-label   { color: #c8d8f0; }

.stButton > button {
    background-color: #1e5aa8 !important; color: white !important;
    border: none; border-radius: 6px;
    font-family: 'EB Garamond', serif; font-size: 1.05rem;
    padding: 0.45rem 2rem;
}
.stButton > button:hover { background-color: #2970cc !important; }
</style>
""", unsafe_allow_html=True)


# ── Petrol price fetcher (no BeautifulSoup – pure requests + simple parse) ──
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_petrol_price() -> float:
    """Fetch current petrol price from OGRA Pakistan. Falls back to latest known rate."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        # Try propakistani which lists current fuel prices in plain text tables
        r = requests.get(
            "https://propakistani.pk/petrol-price-in-pakistan/",
            headers=headers, timeout=8
        )
        text = r.text
        # Find the petrol price row: look for patterns like ">262" or "262.48"
        import re
        # Search for price after "Petrol" keyword within ~300 chars
        idx = text.lower().find("petrol")
        while idx != -1:
            snippet = text[idx: idx + 400]
            matches = re.findall(r'(\d{2,3}\.\d{1,2})', snippet)
            for m in matches:
                val = float(m)
                if 150 < val < 600:   # realistic PKR/litre range
                    return val
            idx = text.lower().find("petrol", idx + 1)
    except Exception:
        pass
    return 262.48   # fallback: OGRA rate June 2025


# ═══════════════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("## 🏦 Bank of Punjab")
st.markdown("### Staff Finance · Debt Burden Calculator")
st.markdown("---")

# Live petrol price
petrol_price = fetch_petrol_price()
st.markdown(
    f'<div class="petrol-banner">⛽ &nbsp;Current Petrol Price (Pakistan): '
    f'<strong>PKR {petrol_price:,.2f} / litre</strong></div>',
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════
#  INPUT SECTION 1 – Monthly Salary
# ═══════════════════════════════════════════════════════════════════════
st.markdown("#### 💼 Monthly Salary")
c1, c2 = st.columns(2)
with c1:
    basic       = st.number_input("Basic Salary (PKR)",           min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
    house_rent  = st.number_input("House Rent Allowance (PKR)",   min_value=0.0, value=0.0,      step=500.0,  format="%.2f")
with c2:
    medical     = st.number_input("Medical Allowance (PKR)",      min_value=0.0, value=0.0,      step=500.0,  format="%.2f")
    other_allow = st.number_input("Other Allowances (PKR)",       min_value=0.0, value=0.0,      step=500.0,  format="%.2f")

monthly_salary = basic + medical + house_rent + other_allow

# ═══════════════════════════════════════════════════════════════════════
#  INPUT SECTION 2 – Monthly Perks
# ═══════════════════════════════════════════════════════════════════════
st.markdown("#### ⛽ Monthly Perks")
c3, c4 = st.columns(2)
with c3:
    petrol_qty  = st.number_input("Petrol Quantity (litres/month)", min_value=0.0, value=100.0, step=5.0,   format="%.1f")
    servant_sal = st.number_input("Servant Salary (PKR)",           min_value=0.0, value=0.0,   step=500.0, format="%.2f")
with c4:
    driver_sal  = st.number_input("Driver Salary (PKR)",            min_value=0.0, value=0.0,   step=500.0, format="%.2f")
    mobile_cost = st.number_input("Mobile Cost (PKR)",              min_value=0.0, value=0.0,   step=100.0, format="%.2f")

petrol_cost         = petrol_qty * petrol_price
total_monthly_perks = petrol_cost + driver_sal + servant_sal + mobile_cost

# ═══════════════════════════════════════════════════════════════════════
#  INPUT SECTION 3 – Existing Loan Deductions
# ═══════════════════════════════════════════════════════════════════════
st.markdown("#### 🏦 Existing Loan Deductions (Monthly Instalments)")
c5, c6, c7 = st.columns(3)
with c5:
    car_inst      = st.number_input("Car Loan (PKR)",      min_value=0.0, value=0.0, step=500.0, format="%.2f")
with c6:
    house_inst    = st.number_input("House Loan (PKR)",    min_value=0.0, value=0.0, step=500.0, format="%.2f")
with c7:
    personal_inst = st.number_input("Personal Loan (PKR)", min_value=0.0, value=0.0, step=500.0, format="%.2f")

total_existing = car_inst + house_inst + personal_inst

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
#  CALCULATE BUTTON
# ═══════════════════════════════════════════════════════════════════════
if st.button("⚙️  Calculate Debt Burden"):

    # ── Calculations ──────────────────────────────────────────────────
    festival_bonus         = basic * 2
    festival_bonus_monthly = festival_bonus / 12

    annual_salary   = monthly_salary * 12
    annual_perks    = total_monthly_perks * 12
    annual_festival = festival_bonus            # paid once per year

    total_annual_salary = annual_salary + annual_perks + annual_festival
    effective_monthly   = total_annual_salary / 12
    total_csr           = total_annual_salary / 2
    monthly_csr         = total_csr / 12

    debt_burden   = monthly_csr - total_existing

    house_cushion = basic * 150
    car_cushion   = basic * 50
    gp_cushion    = basic * 8

    # ── Render helpers ────────────────────────────────────────────────
    SEP = ('<div class="res-sep" style="margin:4px 0">'
           '──────────────────────────────────────────────────────────'
           '</div>')

    def section(title):
        return f'<div class="res-header" style="margin-top:14px">● {title}</div>{SEP}'

    def row(label, value, cls="res-value"):
        return (
            f'<div style="display:flex;justify-content:space-between;padding:3px 0">'
            f'<span class="res-label">{label}</span>'
            f'<span class="{cls}">PKR {value:>16,.2f}</span>'
            f'</div>'
        )

    # ── Build HTML output ─────────────────────────────────────────────
    html = '<div class="result-box">'

    html += section("Monthly Salary Breakdown")
    html += row("Basic Salary",                  basic)
    html += row("Medical Allowance",             medical)
    html += row("House Rent Allowance",          house_rent)
    html += row("Other Allowances",              other_allow)
    html += row("Total Monthly Salary",          monthly_salary)

    html += section("Monthly Perks")
    html += (f'<div style="display:flex;justify-content:space-between;padding:3px 0">'
             f'<span class="res-label">Petrol Rate</span>'
             f'<span class="res-value">PKR {petrol_price:>10,.2f} / litre</span></div>')
    html += row(f"Petrol Cost  ({petrol_qty:.0f} L × {petrol_price:.2f})", petrol_cost)
    html += row("Driver Salary",                 driver_sal)
    html += row("Servant Salary",                servant_sal)
    html += row("Mobile Cost",                   mobile_cost)
    html += row("Total Monthly Perks",           total_monthly_perks)

    html += section("Festival Bonus")
    html += row("Festival Bonus  (Basic × 2)",   festival_bonus)
    html += row("Monthly Amortised  (÷ 12)",     festival_bonus_monthly)

    html += section("Annual Salary Calculation")
    html += row("Annual Salary  (monthly × 12)", annual_salary)
    html += row("Annual Perks   (perks × 12)",   annual_perks)
    html += row("Annual Festival Bonus",         annual_festival)
    html += row("Total Annual Salary",           total_annual_salary)

    html += section("Current Service Ratio (CSR)")
    html += row("Effective Monthly  (Annual ÷ 12)", effective_monthly)
    html += row("Total CSR  (Annual ÷ 2)",          total_csr)
    html += row("Monthly CSR  (CSR ÷ 12)",          monthly_csr)

    html += section("Existing Loan Deductions (Monthly)")
    html += row("Car Loan Instalment",           car_inst)
    html += row("House Loan Instalment",         house_inst)
    html += row("Personal Loan Instalment",      personal_inst)
    html += row("Total Existing Deductions",     total_existing)

    html += section("Debt Burden")
    if debt_burden >= 0:
        html += row("Debt Burden  (Monthly CSR – Deductions)", debt_burden, "res-value")
    else:
        html += row("Debt Burden  ⚠ NEGATIVE – Over-Committed", debt_burden, "res-alert")
        html += ('<div class="res-alert" style="margin-top:6px">'
                 '⚠  Staff member has exceeded repayment capacity.</div>')

    html += section("Maximum Eligible Loan Amounts (Cushions)")
    html += row("House Loan       (150 × Basic Salary)", house_cushion, "res-cushion")
    html += row("Car Loan          (50 × Basic Salary)", car_cushion,   "res-cushion")
    html += row("General Purpose    (8 × Basic Salary)", gp_cushion,    "res-cushion")

    html += SEP + "</div>"
    st.markdown(html, unsafe_allow_html=True)

else:
    st.info("Fill in the fields above and click **⚙️ Calculate Debt Burden** to see results.")

st.markdown("---")
st.caption("Bank of Punjab · Staff Finance Division · Debt Burden Calculator")
