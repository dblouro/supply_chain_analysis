import pandas as pd
import numpy as np

# ── 1. LOAD ───────────────────────────────────────────────
df = pd.read_csv("supply_chain_data.csv")

# ── 2. CLEAN & STANDARDIZE ────────────────────────────────
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Remove duplicate lead time column (keep 'lead_times')
df = df.drop(columns=["lead_time"])

# ── 3. DERIVED FEATURES (KPIs) ────────────────────────────

# Profit margin estimate: revenue - manufacturing costs - shipping costs - other costs
df["total_costs"] = df["manufacturing_costs"] + df["shipping_costs"] + df["costs"]
df["gross_profit"] = df["revenue_generated"] - df["total_costs"]
df["profit_margin_%"] = (df["gross_profit"] / df["revenue_generated"] * 100).round(2)

# Stock turnover: units sold / stock level (higher = more efficient)
df["stock_turnover"] = (df["number_of_products_sold"] / df["stock_levels"].replace(0, np.nan)).round(2)

# Cost per unit sold
df["cost_per_unit"] = (df["total_costs"] / df["number_of_products_sold"]).round(2)

# Defect risk flag
df["high_defect_risk"] = df["defect_rates"] > df["defect_rates"].median()

# ── 4. QUICK SUMMARY ──────────────────────────────────────
print("=== KPI SUMMARY BY PRODUCT TYPE ===")
summary = df.groupby("product_type").agg(
    avg_price=("price", "mean"),
    total_revenue=("revenue_generated", "sum"),
    avg_profit_margin=("profit_margin_%", "mean"),
    avg_stock_turnover=("stock_turnover", "mean"),
    avg_defect_rate=("defect_rates", "mean"),
    avg_lead_time=("lead_times", "mean")
).round(2)
print(summary)

print("\n=== TOP 5 MOST PROFITABLE SKUs ===")
print(df[["sku", "product_type", "gross_profit", "profit_margin_%"]].sort_values("gross_profit", ascending=False).head())

print("\n=== SHIPPING COST BY CARRIER ===")
print(df.groupby("shipping_carriers")["shipping_costs"].mean().round(2))

print("\n=== DEFECT RATE BY SUPPLIER ===")
print(df.groupby("supplier_name")["defect_rates"].mean().round(3).sort_values(ascending=False))