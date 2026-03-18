import pandas as pd
import numpy as np
import sqlite3

# ── LOAD & PREP ───────────────────────────────────────────
df = pd.read_csv("supply_chain_data.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df = df.drop(columns=["lead_time"])
df["total_costs"] = df["manufacturing_costs"] + df["shipping_costs"] + df["costs"]
df["gross_profit"] = df["revenue_generated"] - df["total_costs"]
df["profit_margin_%"] = (df["gross_profit"] / df["revenue_generated"] * 100).round(2)
df["stock_turnover"] = (df["number_of_products_sold"] / df["stock_levels"].replace(0, np.nan)).round(2)
df["cost_per_unit"] = (df["total_costs"] / df["number_of_products_sold"]).round(2)
df["high_defect_risk"] = df["defect_rates"] > df["defect_rates"].median()

# ── EXPORT CSV ────────────────────────────────────────────
df.to_csv("supply_chain_clean.csv", index=False)
print("✓ Clean CSV exported")

# ── SQLITE ────────────────────────────────────────────────
conn = sqlite3.connect("supply_chain.db")
df.to_sql("supply_chain", conn, if_exists="replace", index=False)
print("✓ Data loaded into SQLite")

# ── ANALYTICAL QUERIES ────────────────────────────────────
queries = {
    "Revenue & Margin by Product Type": """
        SELECT product_type,
               ROUND(SUM(revenue_generated), 2) AS total_revenue,
               ROUND(AVG("profit_margin_%"), 2) AS avg_margin_pct,
               ROUND(AVG(stock_turnover), 2) AS avg_stock_turnover
        FROM supply_chain
        GROUP BY product_type
        ORDER BY total_revenue DESC
    """,
    "Supplier Quality Ranking": """
        SELECT supplier_name,
               ROUND(AVG(defect_rates), 3) AS avg_defect_rate,
               ROUND(AVG(manufacturing_costs), 2) AS avg_mfg_cost,
               COUNT(*) AS num_skus
        FROM supply_chain
        GROUP BY supplier_name
        ORDER BY avg_defect_rate ASC
    """,
    "Shipping Cost Efficiency by Mode": """
        SELECT transportation_modes,
               ROUND(AVG(shipping_costs), 2) AS avg_shipping_cost,
               ROUND(AVG(lead_times), 1) AS avg_lead_time,
               COUNT(*) AS num_shipments
        FROM supply_chain
        GROUP BY transportation_modes
        ORDER BY avg_shipping_cost ASC
    """,
    "Top 5 SKUs by Gross Profit": """
        SELECT sku, product_type, supplier_name,
               ROUND(gross_profit, 2) AS gross_profit,
               ROUND("profit_margin_%", 2) AS margin_pct
        FROM supply_chain
        ORDER BY gross_profit DESC
        LIMIT 5
    """,
    "High Defect Risk Products": """
        SELECT sku, product_type, supplier_name,
               ROUND(defect_rates, 3) AS defect_rate,
               ROUND(revenue_generated, 2) AS revenue
        FROM supply_chain
        WHERE high_defect_risk = 1
        ORDER BY defect_rate DESC
        LIMIT 10
    """
}

for title, query in queries.items():
    print(f"\n=== {title} ===")
    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))

conn.close()
print("\n✓ Database connection closed")