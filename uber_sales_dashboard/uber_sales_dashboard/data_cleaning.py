"""
data_cleaning.py
----------------
Standalone script to clean Leaderboard + Attainment Query Data tabs
and export cleaned CSVs for inspection or downstream use.

Run: python data_cleaning.py
"""

import pandas as pd
import numpy as np

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

EXCEL_PATH = "sales_data.xlsx"

# ── Leaderboard ───────────────────────────────────────────────────────────────
print("=== Leaderboard Cleaning ===")
lb = pd.read_excel(EXCEL_PATH, sheet_name="Leaderboard", header=0)

# 1. Drop blank index column
lb = lb.drop(columns=["Unnamed: 0"], errors="ignore")

# 2. Drop fully empty rows
lb = lb.dropna(subset=["Account Executive Name"])

# 3. Strip whitespace from column names
lb.columns = lb.columns.str.strip()

# 4. Normalise categorical fields
lb["Tenure based ramp status"] = lb["Tenure based ramp status"].str.strip().str.title()
lb["Status as of 12/31"]       = lb["Status as of 12/31"].str.strip().str.lower()
lb["Mega Region"]              = lb["Mega Region"].str.strip()
lb["Channel"]                  = lb["Channel"].str.strip()

# 5. Coerce numeric quotas
for col in ["H2'21 NB Quota", "H2'21 CO Quota", "H2 Total Quota"]:
    lb[col] = pd.to_numeric(lb[col], errors="coerce").fillna(0)

# 6. Recalculate Total Quota as NB + CO (guard against stale values)
lb["H2 Total Quota"] = lb["H2'21 NB Quota"] + lb["H2'21 CO Quota"]

print(f"  Rows after cleaning : {len(lb)}")
print(f"  Mega regions        : {lb['Mega Region'].unique().tolist()}")
print(f"  Channels            : {lb['Channel'].unique().tolist()}")
print(f"  Ramp statuses       : {lb['Tenure based ramp status'].unique().tolist()}")
print(f"  Nulls remaining     :\n{lb.isnull().sum()}")

lb.to_csv("leaderboard_clean.csv", index=False)
print("  → leaderboard_clean.csv saved\n")


# ── Attainment Query Data ─────────────────────────────────────────────────────
print("=== Attainment Query Data Cleaning ===")
aq = pd.read_excel(EXCEL_PATH, sheet_name="Attainment Query Data", header=0)
aq.columns = aq.columns.str.strip()

# 1. Drop rows with no AE name
aq = aq.dropna(subset=["Opportunity owner (Account Executive)"])

# 2. Parse dates
aq["Close Date"] = pd.to_datetime(aq["Close Date"], errors="coerce")

# 3. Fill missing Mega Region / Channel from AE-level lookup (Leaderboard)
ae_lookup = lb.set_index("Account Executive Name")[["Mega Region", "Channel"]]
aq = aq.join(ae_lookup.rename(columns={"Mega Region": "MR_lb", "Channel": "Ch_lb"}),
             on="Opportunity owner (Account Executive)")

aq["Mega region"] = aq["Mega region"].fillna(aq["MR_lb"])
aq["Channel"]     = aq["Channel"].fillna(aq["Ch_lb"])
aq = aq.drop(columns=["MR_lb", "Ch_lb"])
# print(aq.columns.tolist())

# print(aq[aq['Opportunity owner (Account Executive)'] == 'Rep68'])
# 4. Normalise text fields
aq["Product"]  = aq["Product"].str.strip().str.lower()
aq["Mega region"] = aq["Mega region"].str.strip()
aq["Channel"]  = aq["Channel"].str.strip()

# 5. Coerce numeric GB columns
for col in ["NB GB (USD)", "CO GB (USD)", "Total $GB (USD)"]:
    aq[col] = pd.to_numeric(aq[col], errors="coerce").fillna(0)

# 6. Recalculate Total GB
aq["Total $GB (USD)"] = aq["NB GB (USD)"] + aq["CO GB (USD)"]

# 7. Classify product type
recurring_products = {"travel", "eats", "central"}
aq["Product Type"] = aq["Product"].apply(
    lambda p: "Recurring" if p in recurring_products else "Non-Recurring"
)

# 8. Add time dimensions
aq["Month"]   = aq["Close Date"].dt.to_period("M").astype(str)
aq["Quarter"] = aq["Close Date"].dt.to_period("Q").astype(str)
aq["Half"]    = aq["Close Date"].dt.month.apply(lambda m: "H1" if m <= 6 else "H2")

print(f"  Rows after cleaning : {len(aq)}")
print(f"  Mega regions        : {aq['Mega region'].dropna().unique().tolist()}")
print(f"  Products            : {aq['Product'].unique().tolist()}")
print(f"  Product types       : {aq['Product Type'].unique().tolist()}")
print(f"  Nulls remaining     :\n{aq.isnull().sum()}")

aq.to_csv("attainment_clean.csv", index=False)
print("  → attainment_clean.csv saved\n")

print("✅ Data cleaning complete.")
