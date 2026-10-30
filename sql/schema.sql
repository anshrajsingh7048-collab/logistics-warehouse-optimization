-- SQLite-compatible schema for the synthetic logistics project.
-- Load the CSVs into tables with the matching names before running queries.
CREATE TABLE IF NOT EXISTS shipments (
  shipment_id TEXT PRIMARY KEY, shipment_date TEXT, route_id TEXT,
  origin TEXT, destination TEXT, transporter_id TEXT,
  truck_capacity_tonnes REAL, quantity_tonnes REAL, distance_km REAL,
  freight_cost_inr REAL, arrival_time_hours REAL, turnaround_minutes REAL,
  on_time_delivery INTEGER, damaged_shipment INTEGER
);
CREATE TABLE IF NOT EXISTS transporters (
  transporter_id TEXT PRIMARY KEY, transporter_name TEXT,
  base_rate_per_tonne_km REAL, reliability_factor REAL
);
CREATE TABLE IF NOT EXISTS warehouses (
  warehouse_id TEXT PRIMARY KEY, warehouse_name TEXT, region TEXT,
  storage_capacity_pallets INTEGER, wsp_name TEXT,
  warehouse_cost_benchmark_per_unit REAL
);
CREATE TABLE IF NOT EXISTS warehouse_operations (
  month TEXT, warehouse_id TEXT, storage_capacity_pallets INTEGER,
  occupied_pallets INTEGER, throughput_units INTEGER,
  avg_handling_minutes REAL, warehouse_cost_per_unit REAL,
  safety_hygiene_audit_score INTEGER
);
CREATE TABLE IF NOT EXISTS inventory (
  snapshot_date TEXT, warehouse_id TEXT, product_id TEXT,
  available_stock_units INTEGER, average_daily_demand_units INTEGER,
  safety_stock_units INTEGER, lead_time_days INTEGER
);
CREATE TABLE IF NOT EXISTS orders (
  order_id TEXT PRIMARY KEY, shipment_id TEXT, warehouse_id TEXT,
  order_date TEXT, promised_delivery_date TEXT, actual_delivery_date TEXT,
  ordered_units INTEGER, delivered_units INTEGER
);
CREATE TABLE IF NOT EXISTS products (
  product_id TEXT PRIMARY KEY, product_name TEXT, category TEXT,
  unit_value_inr REAL, average_daily_demand_units INTEGER, lead_time_days INTEGER
);
CREATE TABLE IF NOT EXISTS cost_benchmarks (
  route_id TEXT PRIMARY KEY, origin TEXT, destination TEXT, distance_km REAL,
  benchmark_freight_per_tonne REAL, benchmark_cost_per_tonne_km REAL
);
