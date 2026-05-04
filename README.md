# 📦 Retail Fulfillment Analyzer

A data analysis project that ingests retail order CSV data, surfaces fulfillment inefficiencies, and generates an interactive HTML dashboard to help operations teams take action.

---

## 🔍 What It Does

- Calculates **KPIs**: delay rate, avg fulfillment time, substitution rate
- Segments performance by **store location**, **hour of day**, **substitution volume**, and **order size**
- Flags **inefficiencies** with severity levels (critical / warning)
- Outputs **actionable recommendations** tied to specific metrics
- Generates a **self-contained interactive dashboard** (`dashboard/index.html`)

---

## 📁 Project Structure

```
retail-fulfillment-analyzer/
├── data/
│   └── retail_orders.csv       # Input dataset
├── analysis/
│   └── analyze.py              # Core analysis engine (no dependencies)
├── dashboard/
│   └── index.html              # Interactive HTML dashboard
├── generate_dashboard.py       # Runs analysis + writes dashboard
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourname/retail-fulfillment-analyzer.git
cd retail-fulfillment-analyzer
```

### 2. Run the analysis + generate dashboard

```bash
python3 generate_dashboard.py
```

Then open `dashboard/index.html` in your browser.

### 3. Run analysis only (JSON output)

```bash
cd analysis
python3 analyze.py
```

---

## 📊 Dataset Schema

| Column | Type | Description |
|---|---|---|
| `Order_ID` | int | Unique order identifier |
| `Order_Time` | datetime | When the order was placed |
| `Delivery_Time` | datetime | When the order was fulfilled |
| `Items_Count` | int | Number of items in the order |
| `Substitutions` | int | Number of substituted items |
| `Store_Location` | string | Fulfillment store (Houston, Dallas, Austin) |
| `Fulfillment_Time_Min` | int | Total minutes from order to delivery |
| `Is_Delayed` | bool | Whether the order exceeded the target SLA |

---

## 💡 Key Findings (Jan 2026 Sample)

| Metric | Value |
|---|---|
| Overall Delay Rate | **50%** ⚠️ |
| Houston Delay Rate | **69.2%** 🔴 |
| 0-substitution orders delayed | **0%** ✅ |
| 5+ substitution orders delayed | **100%** 🔴 |
| Orders with 20+ items delayed | **100%** 🔴 |
| Best fulfillment hour | **8:00 AM** (0% delay) |

---

## 🛠 Requirements

- Python 3.8+
- No external dependencies (pure stdlib)

---

## 📄 License

MIT
