-- 1. Monthly freight spend and shipment volume
SELECT substr(shipment_date, 1, 7) AS month,
       COUNT(*) AS shipment_count,
       ROUND(SUM(freight_cost_inr), 2) AS total_freight_spend_inr,
       ROUND(SUM(quantity_tonnes), 2) AS tonnes_shipped
FROM shipments
GROUP BY substr(shipment_date, 1, 7)
ORDER BY month;

-- 2. Transporter scorecard
SELECT t.transporter_name,
       COUNT(*) AS shipment_count,
       ROUND(SUM(s.freight_cost_inr), 2) AS freight_spend_inr,
       ROUND(SUM(s.freight_cost_inr) / NULLIF(SUM(s.quantity_tonnes), 0), 2) AS freight_cost_per_tonne,
       ROUND(100.0 * AVG(1.0 * s.quantity_tonnes / NULLIF(s.truck_capacity_tonnes, 0)), 1) AS avg_truck_utilization_pct,
       ROUND(100.0 * AVG(s.on_time_delivery), 1) AS on_time_delivery_pct,
       ROUND(AVG(s.turnaround_minutes), 1) AS avg_turnaround_minutes,
       ROUND(100.0 * AVG(s.damaged_shipment), 2) AS damage_rate_pct
FROM shipments s
JOIN transporters t ON t.transporter_id = s.transporter_id
GROUP BY t.transporter_name
ORDER BY freight_cost_per_tonne;

-- 3. Shipments with low truck utilization
SELECT shipment_id, shipment_date, origin, destination, quantity_tonnes,
       truck_capacity_tonnes,
       ROUND(100.0 * quantity_tonnes / NULLIF(truck_capacity_tonnes, 0), 1) AS utilization_pct
FROM shipments
WHERE 100.0 * quantity_tonnes / NULLIF(truck_capacity_tonnes, 0) < 65
ORDER BY utilization_pct;

-- 4. Route cost benchmark screening (benchmark is simulated)
SELECT s.route_id, s.origin, s.destination, COUNT(*) AS shipment_count,
       ROUND(SUM(s.freight_cost_inr), 2) AS actual_spend_inr,
       ROUND(SUM(s.quantity_tonnes * b.benchmark_freight_per_tonne), 2) AS benchmark_spend_inr,
       ROUND(100.0 * (SUM(s.freight_cost_inr) - SUM(s.quantity_tonnes * b.benchmark_freight_per_tonne)) /
             NULLIF(SUM(s.quantity_tonnes * b.benchmark_freight_per_tonne), 0), 1) AS variance_pct
FROM shipments s
JOIN cost_benchmarks b ON b.route_id = s.route_id
GROUP BY s.route_id, s.origin, s.destination
ORDER BY variance_pct DESC;

-- 5. Latest warehouse capacity and operating scorecard
WITH latest_month AS (SELECT MAX(month) AS month FROM warehouse_operations)
SELECT w.warehouse_name, w.region, w.wsp_name, wo.month,
       ROUND(100.0 * wo.occupied_pallets / NULLIF(wo.storage_capacity_pallets, 0), 1) AS space_utilization_pct,
       wo.throughput_units, wo.avg_handling_minutes, wo.warehouse_cost_per_unit,
       w.warehouse_cost_benchmark_per_unit,
       ROUND(100.0 * (wo.warehouse_cost_per_unit - w.warehouse_cost_benchmark_per_unit) /
             NULLIF(w.warehouse_cost_benchmark_per_unit, 0), 1) AS cost_variance_pct,
       wo.safety_hygiene_audit_score
FROM warehouse_operations wo
JOIN warehouses w ON w.warehouse_id = wo.warehouse_id
JOIN latest_month lm ON lm.month = wo.month
ORDER BY space_utilization_pct DESC;

-- 6. WSP performance comparison in the latest month
WITH latest_month AS (SELECT MAX(month) AS month FROM warehouse_operations)
SELECT w.wsp_name, COUNT(DISTINCT wo.warehouse_id) AS warehouse_count,
       ROUND(AVG(100.0 * wo.occupied_pallets / NULLIF(wo.storage_capacity_pallets, 0)), 1) AS avg_space_utilization_pct,
       ROUND(AVG(wo.avg_handling_minutes), 1) AS avg_handling_minutes,
       ROUND(AVG(wo.warehouse_cost_per_unit), 2) AS avg_cost_per_unit,
       ROUND(AVG(wo.safety_hygiene_audit_score), 1) AS avg_audit_score
FROM warehouse_operations wo
JOIN warehouses w ON w.warehouse_id = wo.warehouse_id
JOIN latest_month lm ON lm.month = wo.month
GROUP BY w.wsp_name
ORDER BY avg_cost_per_unit DESC;

-- 7. Latest inventory records below safety stock or at replenishment risk
WITH latest_snapshot AS (SELECT MAX(snapshot_date) AS snapshot_date FROM inventory)
SELECT i.snapshot_date, w.warehouse_name, p.product_name, p.category,
       i.available_stock_units, i.safety_stock_units, i.average_daily_demand_units,
       ROUND(1.0 * i.available_stock_units / NULLIF(i.average_daily_demand_units, 0), 1) AS days_of_cover,
       i.lead_time_days,
       CASE WHEN i.available_stock_units < i.safety_stock_units THEN 1 ELSE 0 END AS below_safety_stock,
       CASE WHEN 1.0 * i.available_stock_units / NULLIF(i.average_daily_demand_units, 0) < i.lead_time_days THEN 1 ELSE 0 END AS replenishment_risk
FROM inventory i
JOIN warehouses w ON w.warehouse_id = i.warehouse_id
JOIN products p ON p.product_id = i.product_id
JOIN latest_snapshot ls ON ls.snapshot_date = i.snapshot_date
WHERE i.available_stock_units < i.safety_stock_units
   OR 1.0 * i.available_stock_units / NULLIF(i.average_daily_demand_units, 0) < i.lead_time_days
ORDER BY days_of_cover;

-- 8. Order service level: on-time, in-full, and OTIF
SELECT COUNT(*) AS total_orders,
       ROUND(100.0 * AVG(CASE WHEN actual_delivery_date <= promised_delivery_date THEN 1.0 ELSE 0.0 END), 1) AS on_time_pct,
       ROUND(100.0 * AVG(CASE WHEN delivered_units >= ordered_units THEN 1.0 ELSE 0.0 END), 1) AS in_full_pct,
       ROUND(100.0 * AVG(CASE WHEN actual_delivery_date <= promised_delivery_date AND delivered_units >= ordered_units THEN 1.0 ELSE 0.0 END), 1) AS otif_pct
FROM orders;

-- 9. Warehouse cost benchmark variance over time
SELECT wo.month, w.warehouse_name,
       ROUND(wo.warehouse_cost_per_unit, 2) AS actual_cost_per_unit,
       ROUND(w.warehouse_cost_benchmark_per_unit, 2) AS benchmark_cost_per_unit,
       ROUND(100.0 * (wo.warehouse_cost_per_unit - w.warehouse_cost_benchmark_per_unit) /
             NULLIF(w.warehouse_cost_benchmark_per_unit, 0), 1) AS variance_pct
FROM warehouse_operations wo
JOIN warehouses w ON w.warehouse_id = wo.warehouse_id
ORDER BY wo.month, variance_pct DESC;

-- 10. Delayed or partially fulfilled orders
SELECT order_id, shipment_id, warehouse_id, promised_delivery_date, actual_delivery_date,
       CAST(julianday(actual_delivery_date) - julianday(promised_delivery_date) AS INTEGER) AS delay_days,
       ordered_units, delivered_units,
       ROUND(100.0 * delivered_units / NULLIF(ordered_units, 0), 1) AS fill_rate_pct
FROM orders
WHERE actual_delivery_date > promised_delivery_date OR delivered_units < ordered_units
ORDER BY delay_days DESC;
