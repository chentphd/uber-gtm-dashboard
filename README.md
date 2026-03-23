# Uber for Business — Sales Performance Dashboard

An Uber-themed Streamlit dashboard for H2 2021 AE performance analysis.  
Answers all five case study questions with interactive charts and AI-ready insights.

---

## Quick Start

### 1. Place your data file
Copy `sales_data.xlsx` (renamed from `Sales_Data_Set_(1)_(3)_(3).xlsx`) into this folder:
```
uber_sales_dashboard/
├── app.py
├── data_cleaning.py
├── requirements.txt
├── README.md
└── sales_data.xlsx   ← put it here
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Run data cleaning script first
```bash
python data_cleaning.py
```
This will export `leaderboard_clean.csv` and `attainment_clean.csv` for inspection.

### 4. Launch the dashboard
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Dashboard Structure

| Tab | Question Addressed |
|---|---|
| 📊 Performance Distribution | AE performance by mega-region; expected vs actual |
| 🎯 Performance Optimization | Right-sizing quotas; ramp status analysis |
| 🔄 Product & Incentives | Recurring vs non-recurring mix; incentive design |
| 💡 Sales Strategy | High-cost AE tradeoffs; deal size vs deal count |
| ⚙️ Scalability & Automation | Architecture, AI/ML roadmap, tech stack |

---

## Sidebar Filters
- **Mega Region** — filter to specific geographies
- **Channel** — ENT / MM / SMB / EXT / Gov
- **Ramp Status** — Fully Ramped / Partially Ramped / No Quota
- **AE Status** — active / inactive / All

All charts update dynamically based on filter selections.

---

## Data Cleaning Summary

### Leaderboard
- Dropped blank index column
- Normalised ramp status capitalisation (`partially ramped` → `Partially Ramped`)
- Coerced quota columns to numeric; filled NAs with 0
- Recalculated `H2 Total Quota = NB Quota + CO Quota`

### Attainment Query Data
- Dropped 276 rows with missing Mega Region — backfilled from Leaderboard AE lookup
- Parsed `Close Date` to datetime
- Normalised `Product` to lowercase
- Classified products into **Recurring** (Travel, Eats, Central) vs **Non-Recurring** (Gift Card, Eats Vouchers, Vouchers)
- Added `Month`, `Quarter`, `Half` time dimensions

---

## Key Insights Surfaced

1. **US&Can dominates quota** (~$31M of $38M total) but attainment variance is wide
2. **~60% of GB is Non-Recurring** — gift cards and vouchers inflate NB without building CO
3. **"Grinder" AEs** chase high deal volume with low GB/deal — need redirection to recurring
4. **276 rows** missing Mega Region in raw data — Salesforce data quality issue to fix
5. **Recurring products generate CO** — every $1 of Travel/Eats NB generates ~$0.8 in next-half CO

---

## Deployment Options

| Platform | Command |
|---|---|
| Local | `streamlit run app.py` |
| Streamlit Community Cloud | Push repo to GitHub → deploy at share.streamlit.io |
| Docker | `docker build -t uber-dashboard . && docker run -p 8501:8501 uber-dashboard` |
| Internal (Heroku/Railway) | Add `Procfile: web: streamlit run app.py --server.port=$PORT` |
