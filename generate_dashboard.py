"""
generate_dashboard.py
Runs the full analysis pipeline and writes a self-contained HTML dashboard.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "analysis"))
from analyze import run_analysis

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "retail_orders.csv")
DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "dashboard")
DASHBOARD_PATH = os.path.join(DASHBOARD_DIR, "index.html")

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fulfillment Intelligence Dashboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

  :root {{
    --bg: #0b0e13;
    --surface: #131720;
    --surface2: #1a2030;
    --border: #252d3d;
    --accent: #00d4aa;
    --accent2: #ff6b6b;
    --accent3: #ffc857;
    --text: #e8edf5;
    --muted: #6b7a99;
    --critical: #ff4d6d;
    --warning: #ffc857;
    --good: #00d4aa;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }}

  /* Grid noise overlay */
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,212,170,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,212,170,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }}

  header {{
    padding: 2.5rem 3rem 2rem;
    border-bottom: 1px solid var(--border);
    position: relative;
    z-index: 1;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
    flex-wrap: wrap;
  }}

  .logo-mark {{
    width: 48px;
    height: 48px;
    background: var(--accent);
    border-radius: 10px;
    display: grid;
    place-items: center;
    font-family: 'DM Mono', monospace;
    font-size: 1.2rem;
    color: var(--bg);
    font-weight: 500;
    flex-shrink: 0;
  }}

  .header-text h1 {{
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1;
  }}

  .header-text p {{
    color: var(--muted);
    font-size: 0.82rem;
    font-family: 'DM Mono', monospace;
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
  }}

  .badge {{
    margin-left: auto;
    padding: 0.35rem 0.9rem;
    border: 1px solid var(--border);
    border-radius: 100px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.08em;
  }}

  main {{
    padding: 2.5rem 3rem;
    position: relative;
    z-index: 1;
    max-width: 1400px;
    margin: 0 auto;
  }}

  .section-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 1rem;
  }}

  /* KPI Grid */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 2.5rem;
  }}

  .kpi-card {{
    background: var(--surface);
    padding: 1.5rem;
    transition: background 0.2s;
  }}

  .kpi-card:hover {{ background: var(--surface2); }}

  .kpi-label {{
    font-size: 0.72rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.05em;
    margin-bottom: 0.6rem;
  }}

  .kpi-value {{
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.03em;
  }}

  .kpi-unit {{
    font-size: 0.9rem;
    font-weight: 400;
    color: var(--muted);
    margin-left: 2px;
  }}

  .kpi-sub {{
    font-size: 0.72rem;
    color: var(--muted);
    margin-top: 0.4rem;
  }}

  /* Flags */
  .flags-grid {{
    display: grid;
    gap: 0.75rem;
    margin-bottom: 2.5rem;
  }}

  .flag {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
  }}

  .flag.critical {{ border-left: 3px solid var(--critical); }}
  .flag.warning {{ border-left: 3px solid var(--warning); }}

  .flag-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
  }}

  .critical .flag-dot {{ background: var(--critical); box-shadow: 0 0 8px var(--critical); }}
  .warning .flag-dot {{ background: var(--warning); box-shadow: 0 0 8px var(--warning); }}

  .flag-content {{ flex: 1; }}

  .flag-header {{
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.35rem;
    flex-wrap: wrap;
  }}

  .flag-metric {{
    font-weight: 500;
    font-size: 0.9rem;
  }}

  .flag-value {{
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
  }}

  .critical .flag-value {{ color: var(--critical); }}
  .warning .flag-value {{ color: var(--warning); }}

  .flag-rec {{
    font-size: 0.8rem;
    color: var(--muted);
    line-height: 1.5;
  }}

  /* Charts section */
  .charts-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2.5rem;
  }}

  @media (max-width: 900px) {{
    .charts-grid {{ grid-template-columns: 1fr; }}
    main {{ padding: 1.5rem; }}
    header {{ padding: 1.5rem; }}
  }}

  .chart-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
  }}

  .chart-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
  }}

  .chart-subtitle {{
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 1.5rem;
  }}

  /* Bar chart */
  .bar-chart {{ display: flex; flex-direction: column; gap: 0.65rem; }}

  .bar-row {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.78rem;
  }}

  .bar-label {{
    width: 70px;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    flex-shrink: 0;
    text-align: right;
  }}

  .bar-track {{
    flex: 1;
    height: 22px;
    background: rgba(255,255,255,0.04);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
  }}

  .bar-fill {{
    height: 100%;
    border-radius: 4px;
    transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    white-space: nowrap;
  }}

  .bar-val {{
    width: 50px;
    text-align: right;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    flex-shrink: 0;
  }}

  /* Scatter / dot matrix */
  .scatter {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 0.5rem;
  }}

  .order-dot {{
    width: 14px;
    height: 14px;
    border-radius: 3px;
    cursor: pointer;
    transition: transform 0.15s, opacity 0.15s;
    position: relative;
  }}

  .order-dot:hover {{
    transform: scale(1.5);
    z-index: 10;
  }}

  .dot-delayed {{ background: var(--critical); opacity: 0.85; }}
  .dot-ontime {{ background: var(--good); opacity: 0.7; }}

  .scatter-legend {{
    display: flex;
    gap: 1.2rem;
    margin-top: 0.8rem;
    font-size: 0.72rem;
    color: var(--muted);
  }}

  .legend-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 2px;
    margin-right: 4px;
    vertical-align: middle;
  }}

  /* Hour heatmap */
  .heatmap {{
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }}

  .heatmap-row {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.75rem;
  }}

  .heatmap-hour {{
    width: 55px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    text-align: right;
    flex-shrink: 0;
  }}

  .heatmap-cell {{
    flex: 1;
    height: 28px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    padding: 0 10px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    transition: filter 0.2s;
  }}

  .heatmap-cell:hover {{ filter: brightness(1.3); }}

  .tooltip {{
    position: fixed;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.15s;
    z-index: 1000;
    line-height: 1.6;
  }}

  .section-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.2rem;
  }}

  .section-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
  }}

  footer {{
    padding: 1.5rem 3rem;
    border-top: 1px solid var(--border);
    font-size: 0.72rem;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    position: relative;
    z-index: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
</style>
</head>
<body>

<header>
  <div class="logo-mark">RF</div>
  <div class="header-text">
    <h1>Fulfillment Intelligence</h1>
    <p>RETAIL ORDER ANALYSIS · JAN 2026</p>
  </div>
  <div class="badge">30 ORDERS · 3 LOCATIONS</div>
</header>

<main>
  <!-- KPIs -->
  <div class="section-label">KEY PERFORMANCE INDICATORS</div>
  <div class="kpi-grid" id="kpiGrid"></div>

  <!-- Flags -->
  <div class="section-header">
    <div class="section-title">🚨 Inefficiency Flags</div>
  </div>
  <div class="flags-grid" id="flagsGrid"></div>

  <!-- Charts -->
  <div class="charts-grid">
    <div class="chart-card">
      <div class="chart-title">Delay Rate by Location</div>
      <div class="chart-subtitle">% of orders exceeding fulfillment SLA</div>
      <div class="bar-chart" id="locationChart"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Substitution Impact</div>
      <div class="chart-subtitle">Avg fulfillment time (min) vs substitution count</div>
      <div class="bar-chart" id="subChart"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Hourly Delay Heatmap</div>
      <div class="chart-subtitle">Delay rate % by hour of day — red = high risk</div>
      <div class="heatmap" id="heatmap"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Order Size vs Delay</div>
      <div class="chart-subtitle">Each square = one order · hover for details</div>
      <div class="scatter" id="scatter"></div>
      <div class="scatter-legend">
        <span><span class="legend-dot" style="background:var(--critical)"></span>Delayed</span>
        <span><span class="legend-dot" style="background:var(--good)"></span>On-time</span>
      </div>
    </div>
  </div>

  <!-- Item count table -->
  <div class="chart-card" style="margin-bottom: 2rem;">
    <div class="chart-title" style="margin-bottom:0.3rem">Order Size Impact</div>
    <div class="chart-subtitle">Fulfillment time and delay rate by item count bucket</div>
    <div class="bar-chart" id="itemChart"></div>
  </div>
</main>

<footer>
  <span>retail-fulfillment-analyzer · generated from retail_orders.csv</span>
  <span>ANALYSIS ENGINE: analyze.py</span>
</footer>

<div class="tooltip" id="tooltip"></div>

<script>
const DATA = __ANALYSIS_JSON__;
const orders = __ORDERS_JSON__;

// KPIs
const kpis = [
  {{ label: "Total Orders", value: DATA.kpis.total_orders, unit: "", sub: "" }},
  {{ label: "Delay Rate", value: DATA.kpis.delay_rate_pct, unit: "%", sub: `${{DATA.kpis.delayed_orders}} of ${{DATA.kpis.total_orders}} delayed`, color: DATA.kpis.delay_rate_pct > 40 ? "var(--critical)" : "var(--good)" }},
  {{ label: "Avg Fulfillment", value: DATA.kpis.avg_fulfillment_min, unit: " min", sub: `Median: ${{DATA.kpis.median_fulfillment_min}} min` }},
  {{ label: "Max Fulfillment", value: DATA.kpis.max_fulfillment_min, unit: " min", sub: "Worst-case order", color: "var(--warning)" }},
  {{ label: "Avg Substitutions", value: DATA.kpis.avg_substitutions, unit: "", sub: `${{DATA.kpis.sub_rate_pct}}% of items substituted` }},
  {{ label: "Avg Items/Order", value: DATA.kpis.avg_items, unit: "", sub: "" }},
  {{ label: "On-Time Orders", value: DATA.kpis.on_time_orders, unit: "", sub: `${{100 - DATA.kpis.delay_rate_pct}}% success rate`, color: "var(--good)" }},
];

const kpiGrid = document.getElementById("kpiGrid");
kpis.forEach(k => {{
  kpiGrid.innerHTML += `
    <div class="kpi-card">
      <div class="kpi-label">${{k.label}}</div>
      <div class="kpi-value" style="color:${{k.color || 'var(--text)'}}">${{k.value}}<span class="kpi-unit">${{k.unit}}</span></div>
      ${{k.sub ? `<div class="kpi-sub">${{k.sub}}</div>` : ''}}
    </div>`;
}});

// Flags
const flagsGrid = document.getElementById("flagsGrid");
DATA.inefficiency_flags.forEach(f => {{
  flagsGrid.innerHTML += `
    <div class="flag ${{f.severity}}">
      <div class="flag-dot"></div>
      <div class="flag-content">
        <div class="flag-header">
          <span class="flag-metric">${{f.metric}}</span>
          <span class="flag-value">${{f.value}} vs threshold ${{f.threshold}}</span>
        </div>
        <div class="flag-rec">→ ${{f.recommendation}}</div>
      </div>
    </div>`;
}});

// Location bar chart (delay rate)
const locationChart = document.getElementById("locationChart");
const locs = Object.entries(DATA.by_location).sort((a,b) => b[1].delay_rate_pct - a[1].delay_rate_pct);
locs.forEach(([loc, d]) => {{
  const pct = d.delay_rate_pct;
  const color = pct > 60 ? "var(--critical)" : pct > 35 ? "var(--warning)" : "var(--good)";
  locationChart.innerHTML += `
    <div class="bar-row">
      <div class="bar-label">${{loc}}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${{pct}}%; background:${{color}}; color: ${{pct > 20 ? '#000' : 'var(--text)'}}">${{pct}}%</div>
      </div>
      <div class="bar-val" style="color:${{color}}">${{d.avg_fulfillment_min}}m</div>
    </div>`;
}});

// Substitution bar chart (avg time)
const subChart = document.getElementById("subChart");
const maxTime = Math.max(...Object.values(DATA.substitution_impact).map(d => d.avg_fulfillment_min));
Object.entries(DATA.substitution_impact).forEach(([label, d]) => {{
  const pct = (d.avg_fulfillment_min / maxTime) * 100;
  const color = d.avg_fulfillment_min > 50 ? "var(--critical)" : d.avg_fulfillment_min > 40 ? "var(--warning)" : "var(--good)";
  subChart.innerHTML += `
    <div class="bar-row">
      <div class="bar-label">subs: ${{label}}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${{pct}}%; background:${{color}}; color: ${{pct > 25 ? '#000' : 'var(--text)'}}">${{d.avg_fulfillment_min}}min</div>
      </div>
      <div class="bar-val" style="color:${{color}}">${{d.delay_rate_pct}}%</div>
    </div>`;
}});

// Heatmap
const heatmap = document.getElementById("heatmap");
Object.entries(DATA.by_hour).forEach(([hour, d]) => {{
  const pct = d.delay_rate_pct;
  const alpha = 0.1 + (pct / 100) * 0.85;
  const r = pct > 50 ? 255 : Math.round(pct * 2.55 * 0.8);
  const g = pct < 50 ? Math.round((100 - pct) * 2.55 * 0.7) : 0;
  const bg = `rgba(${{r}},${{g}},50,${{alpha}})`;
  heatmap.innerHTML += `
    <div class="heatmap-row">
      <div class="heatmap-hour">${{hour.padStart(2,'0')}}:00</div>
      <div class="heatmap-cell" style="background:${{bg}}">
        ${{pct}}% delayed · ${{d.order_count}} orders · avg ${{d.avg_fulfillment_min}}min
      </div>
    </div>`;
}});

// Scatter
const scatter = document.getElementById("scatter");
const tooltip = document.getElementById("tooltip");
const sorted = [...orders].sort((a,b) => a.Items_Count - b.Items_Count);
sorted.forEach(o => {{
  const dot = document.createElement("div");
  dot.className = `order-dot ${{o.Is_Delayed ? 'dot-delayed' : 'dot-ontime'}}`;
  dot.title = `#${{o.Order_ID}}`;
  dot.addEventListener("mousemove", (e) => {{
    tooltip.style.opacity = "1";
    tooltip.style.left = (e.clientX + 14) + "px";
    tooltip.style.top = (e.clientY - 10) + "px";
    tooltip.innerHTML = `Order #${{o.Order_ID}}<br>${{o.Store_Location}} · ${{o.Items_Count}} items<br>Subs: ${{o.Substitutions}} · ${{o.Fulfillment_Time_Min}}min<br>${{o.Is_Delayed ? "⚠ DELAYED" : "✓ ON TIME"}}`;
  }});
  dot.addEventListener("mouseleave", () => {{ tooltip.style.opacity = "0"; }});
  scatter.appendChild(dot);
}});

// Item count chart
const itemChart = document.getElementById("itemChart");
const maxIT = Math.max(...Object.values(DATA.item_count_impact).map(d => d.avg_fulfillment_min));
Object.entries(DATA.item_count_impact).forEach(([label, d]) => {{
  const pct = (d.avg_fulfillment_min / maxIT) * 100;
  const color = d.delay_rate_pct >= 100 ? "var(--critical)" : d.delay_rate_pct > 25 ? "var(--warning)" : "var(--good)";
  itemChart.innerHTML += `
    <div class="bar-row">
      <div class="bar-label">${{label}} items</div>
      <div class="bar-track">
        <div class="bar-fill" style="width:${{pct}}%; background:${{color}}; color: ${{pct > 25 ? '#000' : 'var(--text)'}}">${{d.avg_fulfillment_min}}min</div>
      </div>
      <div class="bar-val" style="color:${{color}}">${{d.delay_rate_pct}}%</div>
    </div>`;
}});
</script>
</body>
</html>
'''


def main():
    print("🔍 Running analysis...")
    results = run_analysis(DATA_PATH)

    # Load raw orders for scatter
    import csv
    orders = []
    with open(DATA_PATH) as f:
        for row in csv.DictReader(f):
            row["Items_Count"] = int(row["Items_Count"])
            row["Substitutions"] = int(row["Substitutions"])
            row["Fulfillment_Time_Min"] = int(row["Fulfillment_Time_Min"])
            row["Is_Delayed"] = row["Is_Delayed"] == "Yes"
            orders.append(row)

    os.makedirs(DASHBOARD_DIR, exist_ok=True)

    html = TEMPLATE.replace(
        "__ANALYSIS_JSON__", json.dumps(results)
    ).replace(
        "__ORDERS_JSON__", json.dumps(orders)
    )

    with open(DASHBOARD_PATH, "w") as f:
        f.write(html)

    print(f"✅ Dashboard written to: {DASHBOARD_PATH}")
    print(f"\n📊 Key findings:")
    k = results["kpis"]
    print(f"   • Delay rate: {k['delay_rate_pct']}%")
    print(f"   • Avg fulfillment: {k['avg_fulfillment_min']} min")
    print(f"   • Flags: {len(results['inefficiency_flags'])} issues detected")
    print(f"\n👉 Open dashboard/index.html in your browser to explore.")


if __name__ == "__main__":
    main()
