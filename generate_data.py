"""Generate reproducible, synthetic FMCG logistics data for the demo project.
All records are simulated and are not affiliated with ITC or any real company.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

warehouses = pd.DataFrame([
    {"warehouse_id": f"WH{i:02d}", "warehouse_name": name, "region": region,
     "storage_capacity_pallets": int(capacity), "wsp_name": wsp,
     "warehouse_cost_benchmark_per_unit": float(bench)}
    for i, (name, region, capacity, wsp, bench) in enumerate([
        ("Jamshedpur DC", "East", 9000, "EastLog Services", 8.2),
        ("Kolkata DC", "East", 12000, "RapidStore Logistics", 7.9),
        ("Patna DC", "East", 7500, "EastLog Services", 8.4),
        ("Ranchi DC", "East", 6500, "Prime Warehousing", 8.1),
        ("Bhubaneswar DC", "East", 8000, "Prime Warehousing", 8.0),
        ("Delhi NCR DC", "North", 15000, "NorthStar 3PL", 7.6),
        ("Lucknow DC", "North", 8500, "NorthStar 3PL", 7.8),
        ("Nagpur DC", "Central", 10000, "CentralLink 3PL", 7.7),
        ("Raipur DC", "Central", 7000, "CentralLink 3PL", 8.3),
        ("Guwahati DC", "Northeast", 6000, "NorthEast Storage", 8.7),
    ], start=1)
])
warehouses.to_csv(DATA / "warehouses.csv", index=False)

transporter_names = ["SwiftHaul", "RoadLink", "BlueRoute", "PrimeMove", "Eastern Carriers", "National Freight", "CargoSphere", "FleetPro", "Reliable Roadways", "TransAxis", "Apex Logistics", "Metro Freight", "OmniHaul", "SpeedLine", "Unity Transport", "Pioneer Carriers", "ExpressWay", "NorthStar Transport"]
transporters = pd.DataFrame({
    "transporter_id": [f"TR{i:02d}" for i in range(1, 19)],
    "transporter_name": transporter_names,
    "base_rate_per_tonne_km": np.round(rng.uniform(1.55, 2.35, 18), 2),
    "reliability_factor": np.round(rng.uniform(0.78, 0.98, 18), 2),
})
transporters.to_csv(DATA / "transporters.csv", index=False)

products = pd.DataFrame({
    "product_id": [f"SKU{i:03d}" for i in range(1, 81)],
    "product_name": [f"FMCG Product {i:03d}" for i in range(1, 81)],
    "category": rng.choice(["Packaged Foods", "Beverages", "Personal Care", "Home Care", "Staples"], 80),
    "unit_value_inr": np.round(rng.uniform(25, 650, 80), 2),
    "average_daily_demand_units": rng.integers(12, 180, 80),
    "lead_time_days": rng.integers(2, 10, 80),
})
products.to_csv(DATA / "products.csv", index=False)

# Route benchmark rates are synthetic benchmark assumptions.
route_pairs = [("Jamshedpur", "Kolkata", 280), ("Jamshedpur", "Patna", 460), ("Jamshedpur", "Ranchi", 130), ("Kolkata", "Bhubaneswar", 440), ("Delhi NCR", "Lucknow", 550), ("Nagpur", "Raipur", 290), ("Patna", "Guwahati", 500), ("Kolkata", "Guwahati", 1030), ("Ranchi", "Bhubaneswar", 450), ("Delhi NCR", "Nagpur", 1050), ("Patna", "Ranchi", 330), ("Nagpur", "Jamshedpur", 700)]
route_rows = []
for origin, destination, distance in route_pairs:
    route_rows.append({"route_id": f"R{len(route_rows)+1:02d}", "origin": origin, "destination": destination,
                       "distance_km": distance, "benchmark_freight_per_tonne": round(distance * 1.78, 2),
                       "benchmark_cost_per_tonne_km": 1.78})
benchmarks = pd.DataFrame(route_rows)
benchmarks.to_csv(DATA / "cost_benchmarks.csv", index=False)

n = 1800
dates = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 303, n), unit="D")
route_idx = rng.integers(0, len(route_pairs), n)
trans_idx = rng.integers(0, len(transporters), n)
truck_caps = rng.choice([5, 9, 14, 18, 24, 30], n, p=[.08, .12, .2, .25, .25, .1])
load_util = np.clip(rng.normal(.76, .18, n), .25, 1.0)
quantity = np.round(truck_caps * load_util, 2)
distance = np.array([route_pairs[i][2] for i in route_idx])
base_rate = transporters.iloc[trans_idx]["base_rate_per_tonne_km"].to_numpy()
route_benchmark = distance * 1.78
freight = quantity * distance * base_rate * rng.normal(1.0, .08, n)
# Add some deliberately high-cost cases for meaningful analysis.
high_cost = rng.random(n) < .12
freight[high_cost] *= rng.uniform(1.15, 1.45, high_cost.sum())
arrival = dates + pd.to_timedelta(rng.integers(5, 16, n), unit="h")
turnaround = np.clip(rng.normal(112, 34, n), 35, 260)
turnaround[rng.random(n) < .12] += rng.uniform(30, 90, (rng.random(n) < .12).sum()) if False else 0
# Use a separate mask to create long-turnaround exceptions.
slow_mask = rng.random(n) < .12
turnaround[slow_mask] += rng.uniform(30, 90, slow_mask.sum())
reliability = transporters.iloc[trans_idx]["reliability_factor"].to_numpy()
on_time = rng.random(n) < np.clip(reliability - (distance / 10000), .55, .98)
damaged = rng.random(n) < .018
shipments = pd.DataFrame({
    "shipment_id": [f"SH{i:05d}" for i in range(1, n+1)],
    "shipment_date": dates.strftime("%Y-%m-%d"),
    "route_id": benchmarks.iloc[route_idx]["route_id"].to_numpy(),
    "origin": [route_pairs[i][0] for i in route_idx],
    "destination": [route_pairs[i][1] for i in route_idx],
    "transporter_id": transporters.iloc[trans_idx]["transporter_id"].to_numpy(),
    "truck_capacity_tonnes": truck_caps,
    "quantity_tonnes": quantity,
    "distance_km": distance,
    "freight_cost_inr": np.round(freight, 2),
    "arrival_time_hours": np.round(rng.uniform(0, 24, n), 2),
    "turnaround_minutes": np.round(turnaround, 1),
    "on_time_delivery": on_time.astype(int),
    "damaged_shipment": damaged.astype(int),
})
shipments.to_csv(DATA / "shipments.csv", index=False)

# Order records linked to shipments; partial fulfilment and delays are deliberately present.
order_n = n
promised_days = rng.integers(1, 5, order_n)
actual_extra = rng.choice([-1, 0, 1, 2, 3], order_n, p=[.06, .63, .18, .09, .04])
order_date = pd.to_datetime(shipments["shipment_date"])
promised = order_date + pd.to_timedelta(promised_days, unit="D")
actual = promised + pd.to_timedelta(actual_extra, unit="D")
ordered = rng.integers(30, 1200, order_n)
fill = np.clip(rng.normal(.97, .08, order_n), .55, 1.0)
delivered = np.floor(ordered * fill).astype(int)
orders = pd.DataFrame({
    "order_id": [f"OR{i:05d}" for i in range(1, order_n+1)],
    "shipment_id": shipments["shipment_id"],
    "warehouse_id": rng.choice(warehouses["warehouse_id"], order_n),
    "order_date": order_date.dt.strftime("%Y-%m-%d"),
    "promised_delivery_date": promised.dt.strftime("%Y-%m-%d"),
    "actual_delivery_date": actual.dt.strftime("%Y-%m-%d"),
    "ordered_units": ordered,
    "delivered_units": delivered,
})
orders.to_csv(DATA / "orders.csv", index=False)

# Warehouse monthly snapshots, one record per warehouse per month.
wh_rows = []
for month in pd.date_range("2026-01-01", "2026-10-01", freq="MS"):
    for _, wh in warehouses.iterrows():
        capacity = int(wh["storage_capacity_pallets"])
        util = float(np.clip(rng.normal(.73, .14), .38, .99))
        if rng.random() < .12:
            util = float(rng.uniform(.91, .99))
        throughput = int(rng.integers(9000, 42000))
        avg_handling = float(np.clip(rng.normal(21, 6), 8, 48))
        cost_per_unit = float(wh["warehouse_cost_benchmark_per_unit"] * rng.normal(1.02, .12))
        wh_rows.append({"month": month.strftime("%Y-%m-%d"), "warehouse_id": wh["warehouse_id"],
                        "storage_capacity_pallets": capacity, "occupied_pallets": int(capacity * util),
                        "throughput_units": throughput, "avg_handling_minutes": round(avg_handling, 1),
                        "warehouse_cost_per_unit": round(cost_per_unit, 2),
                        "safety_hygiene_audit_score": int(np.clip(rng.normal(88, 8), 60, 100))})
warehouse_ops = pd.DataFrame(wh_rows)
warehouse_ops.to_csv(DATA / "warehouse_operations.csv", index=False)

# Inventory snapshots by product and warehouse; demand/stock levels are synthetic.
inv_rows = []
for month in pd.date_range("2026-01-01", "2026-10-01", freq="MS"):
    for _, wh in warehouses.iterrows():
        sample_products = rng.choice(products.index, 35, replace=False)
        for pi in sample_products:
            p = products.iloc[pi]
            daily_demand = int(p["average_daily_demand_units"] * rng.uniform(.7, 1.35))
            stock = int(daily_demand * rng.uniform(1.5, 18))
            safety = int(daily_demand * rng.uniform(4, 8))
            if rng.random() < .1:
                stock = int(daily_demand * rng.uniform(.3, 2.0))
            inv_rows.append({"snapshot_date": month.strftime("%Y-%m-%d"), "warehouse_id": wh["warehouse_id"],
                             "product_id": p["product_id"], "available_stock_units": stock,
                             "average_daily_demand_units": daily_demand, "safety_stock_units": safety,
                             "lead_time_days": int(p["lead_time_days"])})
inventory = pd.DataFrame(inv_rows)
inventory.to_csv(DATA / "inventory.csv", index=False)

# Save metadata and a data dictionary.
print(f"Generated synthetic datasets in {DATA}")
for path in sorted(DATA.glob("*.csv")):
    df = pd.read_csv(path)
    print(f"{path.name}: {len(df):,} rows, {len(df.columns)} columns")
