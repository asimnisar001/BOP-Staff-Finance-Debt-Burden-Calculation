"""
BOP Staff Finance – Debt Burden Calculation App
================================================
Calculates Current Service Ratio (CSR) and maximum eligible
loan amounts for Bank of Punjab staff members.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup


# ──────────────────────────────────────────────
#  Petroleum price scraper (OGRA / PSO)
# ──────────────────────────────────────────────
def fetch_petrol_price() -> float:
    """Try to scrape current petrol price (PKR/litre) from the web.
    Falls back to a hard-coded recent value on failure."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://propakistani.pk/petrol-price-in-pakistan/"
        r = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        # Look for a table cell containing 'Petrol' and grab the next price cell
        for row in soup.find_all("tr"):
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            for i, cell in enumerate(cells):
                if "petrol" in cell.lower() and i + 1 < len(cells):
                    price_text = cells[i + 1].replace(",", "").replace("Rs", "").replace("PKR", "").strip()
                    price = float("".join(c for c in price_text if c.isdigit() or c == "."))
                    if 100 < price < 1000:          # sanity-check
                        return price
    except Exception:
        pass
    return 262.48  # fallback – June 2025 OGRA rate


# ──────────────────────────────────────────────
#  Helper – styled Label/Entry rows
# ──────────────────────────────────────────────
def labeled_entry(parent, label: str, row: int, default: str = "0",
                  bg: str = "#1a2744", fg: str = "#c8d8f0") -> tk.StringVar:
    tk.Label(parent, text=label, bg=bg, fg=fg,
             font=("Georgia", 10), anchor="w", width=34).grid(
        row=row, column=0, sticky="w", padx=(12, 4), pady=4)
    var = tk.StringVar(value=default)
    entry = tk.Entry(parent, textvariable=var, width=16,
                     bg="#0d1b36", fg="#f0e68c", insertbackground="#f0e68c",
                     relief="flat", font=("Consolas", 11), bd=4)
    entry.grid(row=row, column=1, padx=(4, 12), pady=4, sticky="w")
    return var


def section_header(parent, text: str, row: int,
                   bg: str = "#1a2744", span: int = 2):
    tk.Label(parent, text=f"  {text}", bg="#243b6e", fg="#f0c040",
             font=("Georgia", 10, "bold"), anchor="w").grid(
        row=row, column=0, columnspan=span, sticky="ew",
        padx=10, pady=(10, 2), ipady=4)


# ──────────────────────────────────────────────
#  Main Application
# ──────────────────────────────────────────────
class BOPApp(tk.Tk):
    PETROL_DEFAULT = 262.48
    BG_DARK   = "#0d1b36"
    BG_PANEL  = "#1a2744"
    FG_LIGHT  = "#c8d8f0"
    FG_GOLD   = "#f0c040"
    FG_GREEN  = "#44ffaa"
    FG_RED    = "#ff6b6b"
    FG_WHITE  = "#ffffff"

    def __init__(self):
        super().__init__()
        self.title("BOP Staff Finance – Debt Burden Calculator")
        self.configure(bg=self.BG_DARK)
        self.resizable(True, True)
        self.petrol_price = self.PETROL_DEFAULT

        self._build_ui()
        # Fetch live petrol price in background
        threading.Thread(target=self._load_petrol, daemon=True).start()

    # ------------------------------------------------------------------
    def _load_petrol(self):
        price = fetch_petrol_price()
        self.petrol_price = price
        self.petrol_label_var.set(f"₨ {price:.2f} / litre  (live)")

    # ------------------------------------------------------------------
    def _build_ui(self):
        # ── Title bar ──────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#0a1428", pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏦  BANK OF PUNJAB",
                 bg="#0a1428", fg=self.FG_GOLD,
                 font=("Georgia", 16, "bold")).pack()
        tk.Label(hdr, text="Staff Finance  ·  Debt Burden Calculator",
                 bg="#0a1428", fg=self.FG_LIGHT,
                 font=("Georgia", 11)).pack()

        # ── Petrol live price banner ───────────────────────────────────
        pbar = tk.Frame(self, bg="#162040", pady=4)
        pbar.pack(fill="x")
        tk.Label(pbar, text="⛽  Current Petrol Price:",
                 bg="#162040", fg=self.FG_LIGHT,
                 font=("Georgia", 9)).pack(side="left", padx=12)
        self.petrol_label_var = tk.StringVar(value="Fetching …")
        tk.Label(pbar, textvariable=self.petrol_label_var,
                 bg="#162040", fg=self.FG_GREEN,
                 font=("Consolas", 10, "bold")).pack(side="left")

        # ── Scrollable main area ───────────────────────────────────────
        canvas = tk.Canvas(self, bg=self.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=self.BG_DARK)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(e):
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel scrolling
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._build_inputs(inner)

        # ── Buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=self.BG_DARK, pady=10)
        btn_frame.pack(fill="x")

        calc_btn = tk.Button(btn_frame, text="⚙  Calculate",
                             command=self._calculate,
                             bg="#1e5aa8", fg=self.FG_WHITE,
                             font=("Georgia", 11, "bold"),
                             relief="flat", padx=24, pady=6,
                             cursor="hand2", activebackground="#2970cc")
        calc_btn.pack(side="left", padx=20)

        clr_btn = tk.Button(btn_frame, text="↺  Reset",
                            command=self._reset,
                            bg="#4a3000", fg=self.FG_GOLD,
                            font=("Georgia", 10),
                            relief="flat", padx=20, pady=6,
                            cursor="hand2", activebackground="#7a5000")
        clr_btn.pack(side="left", padx=4)

        # ── Results panel ─────────────────────────────────────────────
        self._build_results()

    # ------------------------------------------------------------------
    def _build_inputs(self, parent):
        LEFT_BG = self.BG_PANEL

        # ── Salary ────────────────────────────────────────────────────
        sal = tk.LabelFrame(parent, text="  Monthly Salary  ",
                            bg=LEFT_BG, fg=self.FG_GOLD,
                            font=("Georgia", 10, "bold"), bd=2, relief="groove")
        sal.pack(fill="x", padx=16, pady=8)

        section_header(sal, "Salary Components", 0, bg=LEFT_BG)
        self.v_basic   = labeled_entry(sal, "Basic Salary (PKR)",        1, "100000", LEFT_BG)
        self.v_medical = labeled_entry(sal, "Medical Allowance (PKR)",   2, "0",      LEFT_BG)
        self.v_house   = labeled_entry(sal, "House Rent Allowance (PKR)",3, "0",      LEFT_BG)
        self.v_other   = labeled_entry(sal, "Other Allowances (PKR)",    4, "0",      LEFT_BG)

        # ── Perks ─────────────────────────────────────────────────────
        prk = tk.LabelFrame(parent, text="  Monthly Perks  ",
                            bg=LEFT_BG, fg=self.FG_GOLD,
                            font=("Georgia", 10, "bold"), bd=2, relief="groove")
        prk.pack(fill="x", padx=16, pady=8)

        section_header(prk, "Perks & Benefits", 0, bg=LEFT_BG)
        self.v_petrol_qty     = labeled_entry(prk, "Petrol Quantity (litres/month)", 1, "100", LEFT_BG)
        self.v_driver_sal     = labeled_entry(prk, "Driver Salary (PKR)",            2, "0",   LEFT_BG)
        self.v_servant_sal    = labeled_entry(prk, "Servant Salary (PKR)",           3, "0",   LEFT_BG)
        self.v_mobile_cost    = labeled_entry(prk, "Mobile Cost (PKR)",              4, "0",   LEFT_BG)

        # ── Existing Loans ────────────────────────────────────────────
        lns = tk.LabelFrame(parent, text="  Existing Loan Deductions  ",
                            bg=LEFT_BG, fg=self.FG_GOLD,
                            font=("Georgia", 10, "bold"), bd=2, relief="groove")
        lns.pack(fill="x", padx=16, pady=8)

        section_header(lns, "Monthly Instalments (Already Availed)", 0, bg=LEFT_BG)
        self.v_car_inst      = labeled_entry(lns, "Car Loan Instalment (PKR)",      1, "0", LEFT_BG)
        self.v_house_inst    = labeled_entry(lns, "House Loan Instalment (PKR)",    2, "0", LEFT_BG)
        self.v_personal_inst = labeled_entry(lns, "Personal Loan Instalment (PKR)", 3, "0", LEFT_BG)

    # ------------------------------------------------------------------
    def _build_results(self):
        self.res_frame = tk.LabelFrame(self, text="  Results  ",
                                       bg="#0d1f3c", fg=self.FG_GOLD,
                                       font=("Georgia", 10, "bold"),
                                       bd=2, relief="groove")
        self.res_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.result_text = tk.Text(self.res_frame, bg="#060f22", fg=self.FG_LIGHT,
                                   font=("Consolas", 10), height=28,
                                   relief="flat", wrap="none",
                                   state="disabled")
        vsb = ttk.Scrollbar(self.res_frame, orient="vertical",
                            command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.result_text.pack(fill="both", expand=True, padx=6, pady=6)

        # colour tags
        self.result_text.tag_configure("header",  foreground="#f0c040",
                                       font=("Georgia", 10, "bold"))
        self.result_text.tag_configure("value",   foreground="#44ffaa",
                                       font=("Consolas", 11, "bold"))
        self.result_text.tag_configure("label",   foreground="#c8d8f0",
                                       font=("Consolas", 10))
        self.result_text.tag_configure("sep",     foreground="#334e88")
        self.result_text.tag_configure("alert",   foreground="#ff6b6b",
                                       font=("Consolas", 10, "bold"))
        self.result_text.tag_configure("cushion", foreground="#ffd700",
                                       font=("Consolas", 10))

    # ------------------------------------------------------------------
    def _f(self, var: tk.StringVar) -> float:
        try:
            v = float(var.get().replace(",", ""))
            return max(0.0, v)
        except ValueError:
            return 0.0

    # ------------------------------------------------------------------
    def _calculate(self):
        try:
            self._do_calculate()
        except Exception as exc:
            messagebox.showerror("Calculation Error", str(exc))

    def _do_calculate(self):
        p = self.petrol_price  # PKR/litre

        # ── Monthly Salary ────────────────────────────────────────────
        basic          = self._f(self.v_basic)
        medical        = self._f(self.v_medical)
        house_rent     = self._f(self.v_house)
        other_allow    = self._f(self.v_other)
        monthly_salary = basic + medical + house_rent + other_allow

        # ── Monthly Perks ─────────────────────────────────────────────
        petrol_qty     = self._f(self.v_petrol_qty)
        petrol_cost    = petrol_qty * p
        driver_sal     = self._f(self.v_driver_sal)
        servant_sal    = self._f(self.v_servant_sal)
        mobile_cost    = self._f(self.v_mobile_cost)
        total_monthly_perks = petrol_cost + driver_sal + servant_sal + mobile_cost

        # ── Festival Bonus ────────────────────────────────────────────
        festival_bonus        = basic * 2          # one-time value
        festival_bonus_monthly = festival_bonus / 12  # amortised monthly

        # ── Annual Figures ────────────────────────────────────────────
        annual_salary  = monthly_salary * 12
        annual_perks   = total_monthly_perks * 12
        annual_festival = festival_bonus          # = basic*2 (paid once/year)

        total_annual_salary = annual_salary + annual_perks + annual_festival

        # ── Current Service Ratio (CSR) ───────────────────────────────
        #   "Total Annual Salary / 12"  →  effective monthly all-in
        effective_monthly = total_annual_salary / 12
        #   "Total CSR = Total Annual Salary / 2"
        total_csr = total_annual_salary / 2

        # ── Existing loan deductions ──────────────────────────────────
        car_inst      = self._f(self.v_car_inst)
        house_inst    = self._f(self.v_house_inst)
        personal_inst = self._f(self.v_personal_inst)
        total_existing = car_inst + house_inst + personal_inst

        # Convert annual CSR to monthly for debt burden
        monthly_csr = total_csr / 12

        # ── Debt Burden ───────────────────────────────────────────────
        #   Debt burden = Total CSR (monthly) – existing monthly deductions
        debt_burden = monthly_csr - total_existing

        # ── Loan Cushions ─────────────────────────────────────────────
        house_cushion   = basic * 150
        car_cushion     = basic * 50
        gp_cushion      = basic * 8

        # ── Write results ─────────────────────────────────────────────
        t = self.result_text
        t.configure(state="normal")
        t.delete("1.0", "end")

        SEP = "─" * 62 + "\n"

        def row(label, value, tag_v="value"):
            t.insert("end", f"  {label:<38}", "label")
            t.insert("end", f"PKR {value:>14,.2f}\n", tag_v)

        def hdr(text):
            t.insert("end", f"\n  ● {text}\n", "header")
            t.insert("end", SEP, "sep")

        # MONTHLY SALARY
        hdr("Monthly Salary Breakdown")
        row("Basic Salary",               basic)
        row("Medical Allowance",          medical)
        row("House Rent Allowance",       house_rent)
        row("Other Allowances",           other_allow)
        row("Total Monthly Salary",       monthly_salary)

        # MONTHLY PERKS
        hdr("Monthly Perks")
        t.insert("end", f"  {'Petrol Rate':<38}PKR {p:>14,.2f}  /litre\n", "label")
        row(f"Petrol Cost  ({petrol_qty:.0f} L × {p:.2f})", petrol_cost)
        row("Driver Salary",              driver_sal)
        row("Servant Salary",             servant_sal)
        row("Mobile Cost",                mobile_cost)
        row("Total Monthly Perks",        total_monthly_perks)

        # FESTIVAL BONUS
        hdr("Festival Bonus")
        row("Festival Bonus (Basic × 2)",   festival_bonus)
        row("Monthly Amortised (÷ 12)",     festival_bonus_monthly)

        # ANNUAL
        hdr("Annual Salary Calculation")
        row("Annual Salary  (monthly × 12)",  annual_salary)
        row("Annual Perks   (perks × 12)",    annual_perks)
        row("Annual Festival Bonus",          annual_festival)
        row("Total Annual Salary",            total_annual_salary)

        # CSR
        hdr("Current Service Ratio (CSR)")
        row("Effective Monthly  (Annual ÷ 12)", effective_monthly)
        row("Total CSR  (Annual ÷ 2)",          total_csr)
        row("Monthly CSR  (CSR ÷ 12)",          monthly_csr)

        # EXISTING LOANS
        hdr("Existing Loan Deductions (Monthly)")
        row("Car Loan Instalment",         car_inst)
        row("House Loan Instalment",       house_inst)
        row("Personal Loan Instalment",    personal_inst)
        row("Total Existing Deductions",   total_existing)

        # DEBT BURDEN
        hdr("Debt Burden")
        if debt_burden >= 0:
            t.insert("end", f"  {'Debt Burden (Monthly CSR – Deductions)':<38}", "label")
            t.insert("end", f"PKR {debt_burden:>14,.2f}\n", "value")
        else:
            t.insert("end", f"  {'Debt Burden (NEGATIVE – Over-Committed)':<38}", "label")
            t.insert("end", f"PKR {debt_burden:>14,.2f}\n", "alert")
            t.insert("end", "  ⚠  Staff member has exceeded repayment capacity.\n", "alert")

        # LOAN CUSHIONS
        hdr("Maximum Eligible Loan Amounts (Cushions)")
        t.insert("end", f"  {'House Loan  (150 × Basic)':<38}", "cushion")
        t.insert("end", f"PKR {house_cushion:>14,.2f}\n", "cushion")
        t.insert("end", f"  {'Car Loan    (50 × Basic)':<38}", "cushion")
        t.insert("end", f"PKR {car_cushion:>14,.2f}\n", "cushion")
        t.insert("end", f"  {'General Purpose  (8 × Basic)':<38}", "cushion")
        t.insert("end", f"PKR {gp_cushion:>14,.2f}\n", "cushion")

        t.insert("end", "\n" + SEP, "sep")
        t.configure(state="disabled")

    # ------------------------------------------------------------------
    def _reset(self):
        for var, default in [
            (self.v_basic, "100000"), (self.v_medical, "0"),
            (self.v_house, "0"),      (self.v_other, "0"),
            (self.v_petrol_qty, "100"),
            (self.v_driver_sal, "0"),  (self.v_servant_sal, "0"),
            (self.v_mobile_cost, "0"),
            (self.v_car_inst, "0"),    (self.v_house_inst, "0"),
            (self.v_personal_inst, "0"),
        ]:
            var.set(default)

        t = self.result_text
        t.configure(state="normal")
        t.delete("1.0", "end")
        t.configure(state="disabled")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = BOPApp()
    app.mainloop()

