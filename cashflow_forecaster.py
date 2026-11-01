#!/usr/bin/env python3
"""
MSME AI Cash Flow Forecaster
============================
Practical starter tool for Indian MSMEs.

Helps estimate working capital needs and forecast cash flow shortfalls
using historical sales, collections, expenses, and GST data.

Designed to be simple, readable, and easy to extend with real data sources
(bank statements, GST portal, UPI exports, Account Aggregators).
"""

from datetime import datetime
from typing import List, Dict

# ---------------------------------------------------------------------------
# Sample data for a typical Indian MSME (values in ₹ lakhs for readability)
# Replace with your own numbers or load from CSV/Excel
# ---------------------------------------------------------------------------
SAMPLE_DATA = {
    "business_name": "Sharma Textiles Pvt Ltd",
    "industry": "Manufacturing (Textiles)",
    "historical_months": [
        {"month": "Aug-2026", "sales": 45.0, "collections": 38.0, "expenses": 32.0, "gst_paid": 4.2, "receivables": 22.0, "payables": 15.0},
        {"month": "Sep-2026", "sales": 48.0, "collections": 41.0, "expenses": 34.5, "gst_paid": 4.5, "receivables": 25.0, "payables": 16.5},
        {"month": "Oct-2026", "sales": 52.0, "collections": 44.0, "expenses": 36.0, "gst_paid": 4.8, "receivables": 28.0, "payables": 18.0},
    ],
    "opening_cash": 12.5,          # ₹ lakhs
    "collection_ratio": 0.85,      # typical 85% of sales collected within month + next
    "expense_growth_rate": 0.03,   # 3% monthly growth assumption
    "sales_growth_rate": 0.04,     # 4% monthly growth assumption
}


def calculate_working_capital(latest: Dict) -> float:
    """
    Basic working capital requirement = Receivables + Inventory proxy - Payables
    (Inventory approximated as 30% of monthly expenses for simplicity)
    """
    inventory_proxy = latest["expenses"] * 0.30
    wc = latest["receivables"] + inventory_proxy - latest["payables"]
    return round(wc, 2)


def forecast_cashflow(data: Dict, months_ahead: int = 3) -> List[Dict]:
    """
    Generate simple forward cash flow projection.
    Uses recent averages + growth rates + collection heuristics.
    """
    hist = data["historical_months"]
    avg_sales = sum(m["sales"] for m in hist) / len(hist)
    avg_expenses = sum(m["expenses"] for m in hist) / len(hist)
    avg_gst_ratio = sum(m["gst_paid"] for m in hist) / sum(m["sales"] for m in hist)

    projections = []
    current_cash = data["opening_cash"]
    last_sales = hist[-1]["sales"]
    last_expenses = hist[-1]["expenses"]

    for i in range(1, months_ahead + 1):
        # Project sales and expenses with mild growth
        projected_sales = last_sales * (1 + data["sales_growth_rate"]) ** i
        projected_expenses = last_expenses * (1 + data["expense_growth_rate"]) ** i
        projected_collections = projected_sales * data["collection_ratio"]
        projected_gst = projected_sales * avg_gst_ratio

        # Net cash movement
        net_cash = projected_collections - projected_expenses - projected_gst
        current_cash += net_cash

        projections.append({
            "month": f"M+{i}",
            "projected_sales": round(projected_sales, 2),
            "projected_collections": round(projected_collections, 2),
            "projected_expenses": round(projected_expenses, 2),
            "projected_gst": round(projected_gst, 2),
            "net_cash": round(net_cash, 2),
            "ending_cash": round(current_cash, 2),
        })

    return projections


def generate_recommendations(projections: List[Dict], working_capital: float) -> List[str]:
    """
    Practical, India-specific recommendations based on projections.
    """
    recs = []
    min_cash = min(p["ending_cash"] for p in projections)
    if min_cash < 5.0:  # threshold of ₹5 lakhs
        recs.append("⚠️  Potential cash shortfall detected. Consider:")
        recs.append("   • Offer 2% early payment discount to improve collection ratio")
        recs.append("   • Negotiate 15–30 day extra credit with key suppliers")
        recs.append("   • Time large GST payments after major collections")
        recs.append("   • Explore cash-flow-based working capital loans (many banks now offer these)")
    else:
        recs.append("✅ Cash position looks healthy for the next 3 months.")

    if working_capital > 20:
        recs.append(f"Working capital locked: ₹{working_capital} lakhs. Focus on reducing DSO (Days Sales Outstanding).")

    recs.append("Tip: Reconcile UPI inflows weekly and map them to invoices for better visibility.")
    return recs


def main():
    print("=" * 60)
    print("  MSME AI Cash Flow Forecaster  |  Indian MSME Edition")
    print("=" * 60)
    print(f"Business: {SAMPLE_DATA['business_name']}")
    print(f"Industry: {SAMPLE_DATA['industry']}")
    print(f"As of: {datetime.now().strftime('%d %B %Y')}")
    print()

    latest = SAMPLE_DATA["historical_months"][-1]
    wc = calculate_working_capital(latest)
    print(f"Estimated Working Capital Requirement: ₹{wc} lakhs")
    print()

    projections = forecast_cashflow(SAMPLE_DATA, months_ahead=3)

    print("3-Month Cash Flow Projection (₹ lakhs):")
    print("-" * 60)
    print(f"{'Month':<8} {'Sales':>8} {'Collect':>8} {'Expenses':>8} {'GST':>6} {'Net':>8} {'End Cash':>10}")
    for p in projections:
        print(f"{p['month']:<8} {p['projected_sales']:>8.2f} {p['projected_collections']:>8.2f} "
              f"{p['projected_expenses']:>8.2f} {p['projected_gst']:>6.2f} {p['net_cash']:>8.2f} {p['ending_cash']:>10.2f}")

    print()
    print("Recommendations:")
    for rec in generate_recommendations(projections, wc):
        print(rec)

    print()
    print("Note: This is a starter demo. Replace SAMPLE_DATA with real figures")
    print("or extend the script to read from CSV / bank / GST exports.")
    print("=" * 60)


if __name__ == "__main__":
    main()
