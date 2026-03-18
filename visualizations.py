import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ── LOAD & PREP ───────────────────────────────────────────
df = pd.read_csv("supply_chain_data.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df = df.drop(columns=["lead_time"])
df["total_costs"] = df["manufacturing_costs"] + df["shipping_costs"] + df["costs"]
df["gross_profit"] = df["revenue_generated"] - df["total_costs"]
df["profit_margin_%"] = (df["gross_profit"] / df["revenue_generated"] * 100).round(2)
df["stock_turnover"] = (df["number_of_products_sold"] / df["stock_levels"]).round(2)

# ── STYLE ─────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="Blues_d")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("Supply Chain Performance Dashboard", fontsize=16, fontweight="bold", y=1.01)

# ── CHART 1: Revenue by Product Type ─────────────────────
rev = df.groupby("product_type")["revenue_generated"].sum().reset_index()
sns.barplot(data=rev, x="product_type", y="revenue_generated", hue="product_type", legend=False, ax=axes[0, 0], palette="Blues_d")
axes[0, 0].set_title("Total Revenue by Product Type")
axes[0, 0].set_xlabel("")
axes[0, 0].set_ylabel("Revenue (€)")

# ── CHART 2: Defect Rate by Supplier ─────────────────────
defects = df.groupby("supplier_name")["defect_rates"].mean().reset_index().sort_values("defect_rates", ascending=False)
sns.barplot(data=defects, x="supplier_name", y="defect_rates", hue="supplier_name", legend=False, ax=axes[0, 1], palette="Reds_d")
axes[0, 1].set_title("Avg Defect Rate by Supplier")
axes[0, 1].set_xlabel("")
axes[0, 1].set_ylabel("Defect Rate (%)")

# ── CHART 3: Lead Time Distribution ──────────────────────
sns.histplot(data=df, x="lead_times", hue="product_type", ax=axes[0, 2], bins=15, kde=True)
axes[0, 2].set_title("Lead Time Distribution by Product Type")
axes[0, 2].set_xlabel("Lead Time (days)")

# ── CHART 4: Stock Turnover by Product Type ───────────────
sns.boxplot(data=df, x="product_type", y="stock_turnover", hue="product_type", legend=False, ax=axes[1, 0], palette="Blues_d")
axes[1, 0].set_title("Stock Turnover by Product Type")
axes[1, 0].set_xlabel("")
axes[1, 0].set_ylabel("Stock Turnover Ratio")

# ── CHART 5: Manufacturing Cost vs Revenue ────────────────
sns.scatterplot(data=df, x="manufacturing_costs", y="revenue_generated",
                hue="product_type", size="defect_rates", ax=axes[1, 1], sizes=(40, 200))
axes[1, 1].set_title("Manufacturing Cost vs Revenue")
axes[1, 1].set_xlabel("Manufacturing Cost (€)")
axes[1, 1].set_ylabel("Revenue (€)")

# ── CHART 6: Shipping Cost by Carrier & Mode ─────────────
ship = df.groupby(["shipping_carriers", "transportation_modes"])["shipping_costs"].mean().reset_index()
sns.barplot(data=ship, x="shipping_carriers", y="shipping_costs",
            hue="transportation_modes", ax=axes[1, 2])
axes[1, 2].set_title("Avg Shipping Cost by Carrier & Mode")
axes[1, 2].set_xlabel("")
axes[1, 2].set_ylabel("Shipping Cost (€)")

plt.tight_layout()
plt.savefig("supply_chain_dashboard.png", dpi=150, bbox_inches="tight")
plt.show()
print("Dashboard saved!")