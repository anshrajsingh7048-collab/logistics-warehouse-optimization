from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

st.set_page_config(page_title="Logistics & Warehouse Control Tower", page_icon="📦", layout="wide")

@st.cache_data
def load_data():
    names = ["shipments", "transporters", "warehouses", "warehouse_operations", "inventory", "orders", "products", "cost_benchmarks"]
    return {name: pd.read_csv(DATA / f"{name}.csv") for name in names}

D = load_data()
shipments = D["shipments"].copy()
shipments["shipment_date"] = pd.to_datetime(shipments["shipment_date"])
shipments["truck_utilization_pct"] = shipments["quantity_tonnes"] / shipments["truck_capacity_tonnes"] * 100
shipments["freight_cost_per_tonne"] = shipments["freight_cost_inr"] / shipments["quantity_tonnes"].replace(0, np.nan)
shipments["freight_cost_per_tonne_km"] = shipments["freight_cost_inr"] / (shipments["quantity_tonnes"] * shipments["distance_km"]).replace(0, np.nan)
shipments = shipments.merge(D["transporters"][["transporter_id", "transporter_name"]], on="transporter_id", how="left")
shipments = shipments.merge(D["cost_benchmarks"][["route_id", "benchmark_freight_per_tonne", "benchmark_cost_per_tonne_km"]], on="route_id", how="left")
shipments["benchmark_cost_inr"] = shipments["quantity_tonnes"] * shipments["benchmark_freight_per_tonne"]
shipments["cost_variance_inr"] = shipments["freight_cost_inr"] - shipments["benchmark_cost_inr"]
shipments["cost_variance_pct"] = np.where(shipments["benchmark_cost_inr"] > 0, shipments["cost_variance_inr"] / shipments["benchmark_cost_inr"] * 100, np.nan)

orders = D["orders"].copy()
orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["promised_delivery_date"] = pd.to_datetime(orders["promised_delivery_date"])
orders["actual_delivery_date"] = pd.to_datetime(orders["actual_delivery_date"])
orders["on_time"] = orders["actual_delivery_date"] <= orders["promised_delivery_date"]
orders["in_full"] = orders["delivered_units"] >= orders["ordered_units"]
orders["otif"] = orders["on_time"] & orders["in_full"]

warehouse_ops = D["warehouse_operations"].merge(D["warehouses"][["warehouse_id", "warehouse_name", "region", "wsp_name", "warehouse_cost_benchmark_per_unit"]], on="warehouse_id", how="left")
warehouse_ops["space_utilization_pct"] = warehouse_ops["occupied_pallets"] / warehouse_ops["storage_capacity_pallets"] * 100
warehouse_ops["cost_variance_pct"] = (warehouse_ops["warehouse_cost_per_unit"] - warehouse_ops["warehouse_cost_benchmark_per_unit"]) / warehouse_ops["warehouse_cost_benchmark_per_unit"] * 100
inventory = D["inventory"].merge(D["products"][["product_id", "product_name", "category"]], on="product_id", how="left").merge(D["warehouses"][["warehouse_id", "warehouse_name", "region"]], on="warehouse_id", how="left")
inventory["days_of_cover"] = inventory["available_stock_units"] / inventory["average_daily_demand_units"].replace(0, np.nan)
inventory["below_safety_stock"] = inventory["available_stock_units"] < inventory["safety_stock_units"]
inventory["replenishment_risk"] = inventory["days_of_cover"] < inventory["lead_time_days"]

st.title("📦 Logistics & Warehouse Optimization Control Tower")
st.caption("Portfolio project using simulated FMCG logistics data. Not affiliated with or based on confidential data from ITC or any real company.")

with st.sidebar:
    st.header("Filters")
    min_date = shipments["shipment_date"].min().date()
    max_date = shipments["shipment_date"].max().date()
    date_range = st.date_input("Shipment date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    region_options = ["All"] + sorted(D["warehouses"]["region"].unique().tolist())
    selected_region = st.selectbox("Warehouse region", region_options)
    transporter_options = ["All"] + sorted(shipments["transporter_name"].dropna().unique().tolist())
    selected_transporter = st.selectbox("Transporter", transporter_options)
    st.divider()
    st.caption("All costs are illustrative INR values. Use the README for KPI definitions and assumptions.")

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
else:
    start_date, end_date = shipments["shipment_date"].min(), shipments["shipment_date"].max()
filtered = shipments[(shipments["shipment_date"] >= start_date) & (shipments["shipment_date"] <= end_date)].copy()
if selected_transporter != "All":
    filtered = filtered[filtered["transporter_name"] == selected_transporter]
if selected_region != "All":
    wh_ids = D["warehouses"].loc[D["warehouses"]["region"] == selected_region, "warehouse_id"]
    region_orders = orders[orders["warehouse_id"].isin(wh_ids)]
    region_shipment_ids = set(region_orders["shipment_id"])
    region_filtered = filtered[filtered["shipment_id"].isin(region_shipment_ids)]
    # Shipment records are route-based; if no linked regional orders exist, retain the date/transporter selection and explain it.
    if len(region_filtered):
        filtered = region_filtered

if filtered.empty:
    st.warning("No shipment records match these filters. Change the date range or transporter.")
    st.stop()

page = st.radio("Dashboard", ["Executive Overview", "Transportation", "Warehouse & WSP", "Inventory Risk", "Orders & Service", "Recommendations"], horizontal=True)

if page == "Executive Overview":
    st.subheader("Executive overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Shipments", f"{len(filtered):,}")
    c2.metric("Freight spend", f"₹{filtered['freight_cost_inr'].sum()/100000:.2f} lakh")
    c3.metric("On-time delivery", f"{filtered['on_time_delivery'].mean()*100:.1f}%")
    c4.metric("Avg. truck utilization", f"{filtered['truck_utilization_pct'].mean():.1f}%")
    c5.metric("Avg. turnaround", f"{filtered['turnaround_minutes'].mean():.0f} min")
    left, right = st.columns(2)
    with left:
        monthly = filtered.assign(month=filtered["shipment_date"].dt.to_period("M").astype(str)).groupby("month", as_index=False)["freight_cost_inr"].sum()
        st.markdown("**Monthly freight spend**")
        st.line_chart(monthly.set_index("month"))
    with right:
        by_route = filtered.groupby(["origin", "destination"], as_index=False).agg(freight_spend_inr=("freight_cost_inr", "sum"), avg_utilization_pct=("truck_utilization_pct", "mean"), shipments=("shipment_id", "count")).sort_values("freight_spend_inr", ascending=False).head(10)
        by_route["route"] = by_route["origin"] + " → " + by_route["destination"]
        st.markdown("**Top routes by freight spend**")
        st.bar_chart(by_route.set_index("route")["freight_spend_inr"])
    st.markdown("**Shipment data preview**")
    st.dataframe(filtered[["shipment_id", "shipment_date", "origin", "destination", "transporter_name", "quantity_tonnes", "truck_capacity_tonnes", "truck_utilization_pct", "freight_cost_inr", "turnaround_minutes", "on_time_delivery"]].head(100), use_container_width=True)

elif page == "Transportation":
    st.subheader("Transportation performance & cost")
    a, b, c, d = st.columns(4)
    a.metric("Freight cost / tonne", f"₹{filtered['freight_cost_inr'].sum()/filtered['quantity_tonnes'].sum():,.0f}")
    b.metric("Avg. utilization", f"{filtered['truck_utilization_pct'].mean():.1f}%")
    c.metric("Damage rate", f"{filtered['damaged_shipment'].mean()*100:.2f}%")
    d.metric("Avg. cost variance", f"₹{filtered['cost_variance_inr'].mean():,.0f}/shipment")
    transporter_perf = filtered.groupby("transporter_name", as_index=False).agg(shipments=("shipment_id", "count"), freight_spend_inr=("freight_cost_inr", "sum"), avg_cost_per_tonne=("freight_cost_per_tonne", "mean"), avg_utilization_pct=("truck_utilization_pct", "mean"), on_time_pct=("on_time_delivery", "mean"), avg_turnaround_minutes=("turnaround_minutes", "mean"), damage_rate=("damaged_shipment", "mean"))
    transporter_perf["on_time_pct"] *= 100
    transporter_perf["damage_rate"] *= 100
    st.markdown("**Transporter scorecard**")
    st.dataframe(transporter_perf.sort_values("avg_cost_per_tonne"), use_container_width=True)
    st.markdown("**Truck utilization distribution**")
    st.bar_chart(filtered.assign(util_band=pd.cut(filtered["truck_utilization_pct"], bins=[0, 50, 65, 80, 90, 101], labels=["<50%", "50–65%", "65–80%", "80–90%", ">90%"], include_lowest=True)).groupby("util_band", observed=False).size())
    st.markdown("**Cost outliers: freight cost more than 10% above route benchmark**")
    st.dataframe(filtered[filtered["cost_variance_pct"] > 10][["shipment_id", "origin", "destination", "transporter_name", "quantity_tonnes", "freight_cost_inr", "benchmark_cost_inr", "cost_variance_pct"]].sort_values("cost_variance_pct", ascending=False).head(100), use_container_width=True)

elif page == "Warehouse & WSP":
    st.subheader("Warehouse & service-provider performance")
    wh = warehouse_ops.copy()
    if selected_region != "All":
        wh = wh[wh["region"] == selected_region]
    latest_month = wh["month"].max()
    latest = wh[wh["month"] == latest_month]
    a, b, c, d = st.columns(4)
    a.metric("Warehouses", f"{latest['warehouse_id'].nunique()}")
    b.metric("Avg. space utilization", f"{latest['space_utilization_pct'].mean():.1f}%")
    c.metric("Avg. handling time", f"{latest['avg_handling_minutes'].mean():.1f} min")
    d.metric("Avg. audit score", f"{latest['safety_hygiene_audit_score'].mean():.1f}/100")
    st.markdown("**Latest warehouse snapshot**")
    st.dataframe(latest[["warehouse_name", "region", "wsp_name", "space_utilization_pct", "throughput_units", "avg_handling_minutes", "warehouse_cost_per_unit", "warehouse_cost_benchmark_per_unit", "cost_variance_pct", "safety_hygiene_audit_score"]].sort_values("space_utilization_pct", ascending=False), use_container_width=True)
    wsp = latest.groupby("wsp_name", as_index=False).agg(warehouses=("warehouse_id", "nunique"), avg_space_utilization_pct=("space_utilization_pct", "mean"), avg_handling_minutes=("avg_handling_minutes", "mean"), avg_cost_per_unit=("warehouse_cost_per_unit", "mean"), avg_cost_variance_pct=("cost_variance_pct", "mean"), avg_audit_score=("safety_hygiene_audit_score", "mean"))
    st.markdown("**WSP scorecard**")
    st.dataframe(wsp.sort_values("avg_cost_variance_pct", ascending=False), use_container_width=True)
    st.markdown("**Warehouse space utilization by month**")
    trend = wh.groupby("month", as_index=False)["space_utilization_pct"].mean()
    st.line_chart(trend.set_index("month"))

elif page == "Inventory Risk":
    st.subheader("Inventory norms & replenishment risk")
    inv = inventory.copy()
    if selected_region != "All":
        inv = inv[inv["region"] == selected_region]
    latest_date = inv["snapshot_date"].max()
    latest = inv[inv["snapshot_date"] == latest_date].copy()
    a, b, c, d = st.columns(4)
    a.metric("SKU-location records", f"{len(latest):,}")
    b.metric("Below safety stock", f"{latest['below_safety_stock'].mean()*100:.1f}%")
    c.metric("Lead-time risk", f"{latest['replenishment_risk'].mean()*100:.1f}%")
    d.metric("Avg. stock cover", f"{latest['days_of_cover'].mean():.1f} days")
    st.markdown("**Highest-priority replenishment risks**")
    risk = latest[latest["replenishment_risk"] | latest["below_safety_stock"]].copy()
    risk["risk_reason"] = np.select([risk["below_safety_stock"] & risk["replenishment_risk"], risk["below_safety_stock"], risk["replenishment_risk"]], ["Below safety stock + lead-time risk", "Below safety stock", "Lead-time risk"], default="Review")
    st.dataframe(risk.sort_values(["below_safety_stock", "days_of_cover"], ascending=[False, True])[["warehouse_name", "product_id", "product_name", "category", "available_stock_units", "safety_stock_units", "average_daily_demand_units", "days_of_cover", "lead_time_days", "risk_reason"]].head(200), use_container_width=True)
    st.markdown("**Stock cover distribution**")
    st.bar_chart(latest.assign(cover_band=pd.cut(latest["days_of_cover"], bins=[0, 2, 5, 8, 14, 1000], labels=["0–2 days", "2–5 days", "5–8 days", "8–14 days", "14+ days"], include_lowest=True)).groupby("cover_band", observed=False).size())

elif page == "Orders & Service":
    st.subheader("Customer service and order fulfilment")
    selected_orders = orders.copy()
    selected_orders = selected_orders[(selected_orders["order_date"] >= start_date) & (selected_orders["order_date"] <= end_date)]
    if selected_region != "All":
        ids = D["warehouses"].loc[D["warehouses"]["region"] == selected_region, "warehouse_id"]
        selected_orders = selected_orders[selected_orders["warehouse_id"].isin(ids)]
    a, b, c, d = st.columns(4)
    a.metric("Orders", f"{len(selected_orders):,}")
    b.metric("On-time", f"{selected_orders['on_time'].mean()*100:.1f}%" if len(selected_orders) else "—")
    c.metric("In-full", f"{selected_orders['in_full'].mean()*100:.1f}%" if len(selected_orders) else "—")
    d.metric("OTIF", f"{selected_orders['otif'].mean()*100:.1f}%" if len(selected_orders) else "—")
    selected_orders["fill_rate_pct"] = selected_orders["delivered_units"] / selected_orders["ordered_units"].replace(0, np.nan) * 100
    selected_orders["delivery_delay_days"] = (selected_orders["actual_delivery_date"] - selected_orders["promised_delivery_date"]).dt.days
    st.markdown("**Delivery delay distribution (days)**")
    st.bar_chart(selected_orders["delivery_delay_days"].value_counts().sort_index())
    st.markdown("**Orders requiring review**")
    st.dataframe(selected_orders[(~selected_orders["on_time"]) | (~selected_orders["in_full"])][["order_id", "shipment_id", "warehouse_id", "promised_delivery_date", "actual_delivery_date", "ordered_units", "delivered_units", "fill_rate_pct", "delivery_delay_days"]].head(150), use_container_width=True)

else:
    st.subheader("Actionable recommendations")
    recommendations = []
    low_util = filtered[filtered["truck_utilization_pct"] < 65]
    if len(low_util):
        recommendations.append({"priority": "High", "area": "Transportation", "finding": f"{len(low_util):,} shipments have truck utilization below 65%.", "recommended_action": "Review route schedules and shipment consolidation opportunities while respecting delivery windows, product compatibility and truck constraints."})
    high_cost = filtered[filtered["cost_variance_pct"] > 10]
    if len(high_cost):
        recommendations.append({"priority": "High", "area": "Freight cost", "finding": f"{len(high_cost):,} shipments cost more than 10% above the route benchmark.", "recommended_action": "Audit rate cards, distance assumptions, vehicle type, load factor and accessorial charges before renegotiating or changing allocation."})
    slow = filtered[filtered["turnaround_minutes"] > 150]
    if len(slow):
        recommendations.append({"priority": "Medium", "area": "Turnaround", "finding": f"{len(slow):,} shipments show turnaround above 150 minutes.", "recommended_action": "Separate gate waiting, dock waiting, loading and paperwork time; test appointment slots and shift planning."})
    wh_latest = warehouse_ops[warehouse_ops["month"] == warehouse_ops["month"].max()]
    if selected_region != "All":
        wh_latest = wh_latest[wh_latest["region"] == selected_region]
    high_space = wh_latest[wh_latest["space_utilization_pct"] > 90]
    if len(high_space):
        recommendations.append({"priority": "Medium", "area": "Warehouse capacity", "finding": f"{len(high_space)} warehouse(s) exceed 90% space utilization in the latest snapshot.", "recommended_action": "Validate slotting, dead stock, peak-season capacity and overflow options before committing extra space."})
    inv_latest = inventory[inventory["snapshot_date"] == inventory["snapshot_date"].max()]
    if selected_region != "All":
        inv_latest = inv_latest[inv_latest["region"] == selected_region]
    inv_risk = inv_latest[inv_latest["replenishment_risk"] | inv_latest["below_safety_stock"]]
    if len(inv_risk):
        recommendations.append({"priority": "High", "area": "Inventory", "finding": f"{len(inv_risk):,} SKU-location records are below safety stock or have stock cover below lead time.", "recommended_action": "Review forecast, replenishment lead time, minimum order quantity and transfer options; validate before raising purchase orders."})
    if not recommendations:
        recommendations.append({"priority": "Review", "area": "Monitoring", "finding": "No threshold-based issue found for the current filters.", "recommended_action": "Review other date windows and confirm thresholds reflect the business context."})
    st.info("Recommendations are rule-based prompts generated from this synthetic dataset. They are not automated operational instructions.")
    st.dataframe(pd.DataFrame(recommendations), use_container_width=True, hide_index=True)
    st.markdown("**Scenario calculator: estimated freight savings**")
    target_reduction = st.slider("Assumed reducible share of current freight spend (%)", min_value=0, max_value=20, value=5, step=1)
    baseline = filtered["freight_cost_inr"].sum()
    estimated = baseline * target_reduction / 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Current freight spend", f"₹{baseline:,.0f}")
    c2.metric("Assumed reduction", f"{target_reduction}%")
    c3.metric("Illustrative savings", f"₹{estimated:,.0f}")
    st.caption("This is a scenario estimate only, not a forecast or guaranteed saving. Validate operational feasibility and service impacts before applying changes.")

st.divider()
st.caption("Demo note: Synthetic data generated with a fixed random seed for reproducibility. Metrics, benchmarks, thresholds and examples are illustrative; they are not ITC performance data.")
