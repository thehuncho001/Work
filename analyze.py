"""
Retail Order Fulfillment Analysis
Identifies inefficiencies and generates insights to improve fulfillment performance.
"""

import csv
import json
from datetime import datetime
from collections import defaultdict
import statistics


def load_data(filepath):
    orders = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["Items_Count"] = int(row["Items_Count"])
            row["Substitutions"] = int(row["Substitutions"])
            row["Fulfillment_Time_Min"] = int(row["Fulfillment_Time_Min"])
            row["Is_Delayed"] = row["Is_Delayed"] == "Yes"
            row["Order_Time"] = datetime.strptime(row["Order_Time"], "%Y-%m-%d %H:%M")
            row["Delivery_Time"] = datetime.strptime(row["Delivery_Time"], "%Y-%m-%d %H:%M")
            row["Hour"] = row["Order_Time"].hour
            row["Day"] = row["Order_Time"].strftime("%Y-%m-%d")
            orders.append(row)
    return orders


def overall_kpis(orders):
    total = len(orders)
    delayed = sum(1 for o in orders if o["Is_Delayed"])
    times = [o["Fulfillment_Time_Min"] for o in orders]
    subs = [o["Substitutions"] for o in orders]
    items = [o["Items_Count"] for o in orders]
    return {
        "total_orders": total,
        "delayed_orders": delayed,
        "on_time_orders": total - delayed,
        "delay_rate_pct": round(delayed / total * 100, 1),
        "avg_fulfillment_min": round(statistics.mean(times), 1),
        "median_fulfillment_min": statistics.median(times),
        "max_fulfillment_min": max(times),
        "min_fulfillment_min": min(times),
        "avg_substitutions": round(statistics.mean(subs), 2),
        "avg_items": round(statistics.mean(items), 1),
        "sub_rate_pct": round(sum(subs) / sum(items) * 100, 1),
    }


def by_location(orders):
    loc_data = defaultdict(list)
    for o in orders:
        loc_data[o["Store_Location"]].append(o)

    result = {}
    for loc, group in loc_data.items():
        times = [o["Fulfillment_Time_Min"] for o in group]
        delayed = sum(1 for o in group if o["Is_Delayed"])
        subs = [o["Substitutions"] for o in group]
        result[loc] = {
            "total_orders": len(group),
            "delayed_orders": delayed,
            "delay_rate_pct": round(delayed / len(group) * 100, 1),
            "avg_fulfillment_min": round(statistics.mean(times), 1),
            "avg_substitutions": round(statistics.mean(subs), 2),
        }
    return result


def by_hour(orders):
    hour_data = defaultdict(list)
    for o in orders:
        hour_data[o["Hour"]].append(o)

    result = {}
    for hour in sorted(hour_data.keys()):
        group = hour_data[hour]
        times = [o["Fulfillment_Time_Min"] for o in group]
        delayed = sum(1 for o in group if o["Is_Delayed"])
        result[str(hour)] = {
            "order_count": len(group),
            "delayed_count": delayed,
            "delay_rate_pct": round(delayed / len(group) * 100, 1),
            "avg_fulfillment_min": round(statistics.mean(times), 1),
        }
    return result


def substitution_impact(orders):
    buckets = {"0": [], "1-2": [], "3-4": [], "5+": []}
    for o in orders:
        s = o["Substitutions"]
        if s == 0:
            buckets["0"].append(o)
        elif s <= 2:
            buckets["1-2"].append(o)
        elif s <= 4:
            buckets["3-4"].append(o)
        else:
            buckets["5+"].append(o)

    result = {}
    for label, group in buckets.items():
        if group:
            times = [o["Fulfillment_Time_Min"] for o in group]
            delayed = sum(1 for o in group if o["Is_Delayed"])
            result[label] = {
                "order_count": len(group),
                "avg_fulfillment_min": round(statistics.mean(times), 1),
                "delay_rate_pct": round(delayed / len(group) * 100, 1),
            }
    return result


def item_count_impact(orders):
    buckets = {"1-9": [], "10-14": [], "15-19": [], "20+": []}
    for o in orders:
        ic = o["Items_Count"]
        if ic < 10:
            buckets["1-9"].append(o)
        elif ic < 15:
            buckets["10-14"].append(o)
        elif ic < 20:
            buckets["15-19"].append(o)
        else:
            buckets["20+"].append(o)

    result = {}
    for label, group in buckets.items():
        if group:
            times = [o["Fulfillment_Time_Min"] for o in group]
            delayed = sum(1 for o in group if o["Is_Delayed"])
            result[label] = {
                "order_count": len(group),
                "avg_fulfillment_min": round(statistics.mean(times), 1),
                "delay_rate_pct": round(delayed / len(group) * 100, 1),
            }
    return result


def inefficiency_flags(orders):
    flags = []
    kpis = overall_kpis(orders)

    if kpis["delay_rate_pct"] > 40:
        flags.append({
            "severity": "critical",
            "metric": "Overall Delay Rate",
            "value": f"{kpis['delay_rate_pct']}%",
            "threshold": "40%",
            "recommendation": "Investigate root causes — staffing, route optimization, or inventory shortages may be culprits."
        })

    loc = by_location(orders)
    for store, data in loc.items():
        if data["delay_rate_pct"] > 60:
            flags.append({
                "severity": "critical",
                "metric": f"{store} Delay Rate",
                "value": f"{data['delay_rate_pct']}%",
                "threshold": "60%",
                "recommendation": f"Prioritize {store}: audit picker routing, staffing levels, and local inventory."
            })
        if data["avg_substitutions"] > 4:
            flags.append({
                "severity": "warning",
                "metric": f"{store} Avg Substitutions",
                "value": str(data["avg_substitutions"]),
                "threshold": "4.0",
                "recommendation": f"Improve {store} inventory forecasting to reduce substitutions."
            })

    by_h = by_hour(orders)
    for hour, data in by_h.items():
        if data["delay_rate_pct"] > 80:
            flags.append({
                "severity": "warning",
                "metric": f"Hour {hour}:00 Delay Rate",
                "value": f"{data['delay_rate_pct']}%",
                "threshold": "80%",
                "recommendation": f"Add picker capacity between {hour}:00–{int(hour)+1}:00 to manage peak-hour surge."
            })

    sub_imp = substitution_impact(orders)
    if "5+" in sub_imp and sub_imp["5+"]["avg_fulfillment_min"] > 60:
        flags.append({
            "severity": "warning",
            "metric": "High-Sub Orders Fulfillment Time",
            "value": f"{sub_imp['5+']['avg_fulfillment_min']} min",
            "threshold": "60 min",
            "recommendation": "Orders with 5+ substitutions average >60 min. Introduce a substitution cap or pre-approval flow."
        })

    return flags


def run_analysis(filepath):
    orders = load_data(filepath)
    return {
        "kpis": overall_kpis(orders),
        "by_location": by_location(orders),
        "by_hour": by_hour(orders),
        "substitution_impact": substitution_impact(orders),
        "item_count_impact": item_count_impact(orders),
        "inefficiency_flags": inefficiency_flags(orders),
    }


if __name__ == "__main__":
    results = run_analysis("../data/retail_orders.csv")
    print(json.dumps(results, indent=2))
