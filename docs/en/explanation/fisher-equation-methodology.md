# Explanation: Focus Methodology and Fisher Equation

This document outlines the macroeconomic, theoretical, and mathematical foundations underpinning the **Focus Market Intelligence** platform, with particular focus on Central Bank of Brazil survey dynamics and the formal derivation of the **ex-ante real interest rate**.

---

## Central Bank Market Expectations System (Focus)

The Central Bank of Brazil (BCB) monitors market expectations daily via an automated survey collecting projections from over 100 banks, brokerages, asset management firms, and economic consultancies.

### Survey Frequency: Daily vs. Weekly
* **Weekly Focus Bulletin (PDF):** Released every Monday morning, summarizing survey distributions up to the preceding Friday close.
* **Olinda OData API (Business-Day Granularity):** The underlying database records and updates projections on a **business-day** cadence. Participating institutions update forecast models continuously, allowing daily tracking of sentiment shifts.

### Calculation Base Windows
1. **Base 0 (30 Calendar Days Window):** Used in the *Panorama Focus* (Page 1). Considers projections updated by participants within the last 30 calendar days for calendar target years (e.g., year-end 2026).
2. **Base 1 (5 Business Days Window):** Used in the real interest rate calculation and 12-month smoothed inflation (Page 3). Considers only projections revised within the last 5 business days, providing immediate sensitivity to policy signals and macro shocks.

---

## The Top 5 Group: Purpose and Mechanism

The Central Bank publishes rankings identifying the top 5 institutions exhibiting the highest forecast accuracy for core indicators (IPCA, Selic, Exchange Rate, and IGP-M).
* **Strategic Relevance:** Comparing broad market medians against the Top 5 uncovers consensus anchoring and early divergence. When Top 5 institutions hold substantially more aggressive (*Hawkish*) expectations than the broad market, broader consensus typically revises upward in subsequent weeks.

---

## The Fisher Equation: Rigorous Ex-Ante Real Rate

The real interest rate represents the nominal rate adjusted for expected inflation. Irving Fisher's foundational relation states:

$$(1 + i) = (1 + r)(1 + \pi^e)$$

Where:
* $i$ = Effective nominal interest rate (% p.a.) — Copom target Selic rate.
* $r$ = Ex-ante real interest rate (% p.a.).
* $\pi^e$ = Expected inflation over the next 12 rolling months (% p.a.) — 12-month smoothed IPCA expectation.

Solving for real rate $r$:

$$r = \left( \frac{1 + \frac{i}{100}}{1 + \frac{\pi^e}{100}} - 1 \right) \times 100$$

---

### Why Linear Subtraction ($r \approx i - \pi$) Fails in High-Rate Economies

In developed economies with low nominal rates and inflation around 2%, linear approximation ($r \approx i - \pi$) introduces minimal error.

However, in emerging economies with double-digit nominal rates like Brazil, linear subtraction produces an **unacceptable distortion**:

#### Real-World Example with Platform Data (October 2026):
* **Effective Selic ($i$):** $13.75\%$
* **Expected 12M Inflation ($\pi^e$):** $4.65\%$

1. **Simplistic Linear Subtraction:**
   $$r_{\text{linear}} = 13.75\% - 4.65\% = \mathbf{9.10\%}$$

2. **Exact Fisher Equation (Implemented in dbt and Dashboard):**
   $$r_{\text{Fisher}} = \left( \frac{1 + 0.1375}{1 + 0.0465} - 1 \right) \times 100 = \left( \frac{1.1375}{1.0465} - 1 \right) \times 100 = \mathbf{8.6956\% \approx 8.69\%}$$

> **Impact:** The linear approximation overstates Brazil's real interest rate by **+0.41 percentage points (41 basis points)**. In sovereign risk assessment, corporate cost of capital (WACC), and inflation-linked bond pricing (NTN-B), a 41 bps error significantly distorts asset valuation.

---

## Why "Ex-Ante"?
* **Ex-Post Real Rate:** Backward-looking. Deflates realized nominal returns against past inflation. Measures historical returns.
* **Ex-Ante Real Rate:** Forward-looking. Deflates nominal rates against **expected future inflation** over the next 12 months. This metric determines the true stance of monetary policy, financial conditions tightening, and corporate capital investment decisions.
