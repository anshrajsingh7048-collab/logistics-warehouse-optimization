# Logistics & Warehouse Optimization Control Tower

An end-to-end portfolio project designed around common FMCG logistics and warehousing responsibilities: freight spend, truck utilization, transporter performance, warehouse service-provider performance, inventory norms, stockout risk, order fulfilment, and operational improvement opportunities.

> **Important data disclaimer:** This is an independent portfolio project using entirely synthetic data. It is not affiliated with ITC and does not use ITC's confidential or internal data. All costs, benchmark rates, locations, performance figures, and example findings are simulated.

## Features

- Executive overview with shipment, freight, delivery, utilization, and turnaround KPIs
- Transportation analysis by route and transporter
- Freight benchmark variance and high-cost shipment identification
- Warehouse/WSP scorecards: space utilization, throughput, handling time, cost variance, and safety/hygiene audit score
- Inventory norms: stock cover, safety-stock violations, and replenishment risk
- Customer service: on-time, in-full, and OTIF measures
- Rule-based recommendations and an illustrative savings scenario calculator
- SQL schema and query library for demonstrating data-analysis capability

## Technology

- Python, Pandas, NumPy
- Streamlit
- SQL (SQLite-compatible query examples)
- CSV datasets; GitHub for source control and Streamlit Community Cloud for deployment

## Run locally

1. Install Python 3.10 or later.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

The app loads the supplied CSVs from the `data/` directory. Internet access is not required after dependencies are installed.

## Regenerate the synthetic data

```bash
python generate_data.py
```

The generator uses a fixed random seed, so the dataset is reproducible. It creates:

| File | Purpose | Approximate rows |
|---|---|---:|
| `shipments.csv` | Shipment-level transport cost and service metrics | 1,800 |
| `transporters.csv` | Transporter reference data | 18 |
| `warehouses.csv` | Warehouse/WSP reference data | 10 |
| `warehouse_operations.csv` | Monthly warehouse snapshots | 100 |
| `inventory.csv` | Monthly product-warehouse inventory snapshots | 3,500 |
| `orders.csv` | Order promise, actual delivery, and fill quantities | 1,800 |
| `products.csv` | Product and demand reference data | 80 |
| `cost_benchmarks.csv` | Route benchmark assumptions | 12 |

## Dashboard pages

1. **Executive Overview:** freight spend, on-time delivery, truck utilization, turnaround, monthly cost trends, and top routes.
2. **Transportation:** transporter scorecard, cost per tonne, utilization distribution, damage rate, and cost outliers.
3. **Warehouse & WSP:** storage utilization, throughput, handling time, warehouse cost variance, and audit score.
4. **Inventory Risk:** stock cover, safety-stock violations, and SKU-location replenishment risk.
5. **Orders & Service:** on-time, in-full, OTIF, delivery delays, and orders requiring review.
6. **Recommendations:** threshold-based prompts and a user-adjustable savings scenario.

## KPI definitions

- **Truck utilization (%)** = quantity loaded in tonnes / truck capacity in tonnes × 100.
- **Freight cost per tonne** = freight spend / tonnes shipped.
- **On-time delivery (%)** = shipment records marked on time / shipment records × 100.
- **Truck turnaround (minutes)** = simulated total truck turnaround duration from arrival through loading/unloading and departure. The synthetic dataset stores this as one measure.
- **Warehouse space utilization (%)** = occupied pallet positions / usable storage capacity × 100.
- **Days of cover** = available stock / average daily demand.
- **Below safety stock** = available stock < safety stock.
- **Replenishment risk** = days of cover < replenishment lead time.
- **In-full** = delivered units ≥ ordered units.
- **OTIF (%)** = orders delivered on or before promised date and in full / eligible orders × 100.
- **Freight benchmark variance** = actual freight spend − simulated quantity × route benchmark freight per tonne. Since the benchmark is an assumption, interpret the comparison as a screening signal, not proof of overcharging.
- **Warehouse cost variance (%)** = (actual simulated cost per unit − benchmark cost per unit) / benchmark cost per unit × 100.

## Important assumptions and limitations

- Synthetic data is designed for demonstration and is not a statistically representative model of any real company.
- Shipment on-time status and order delivery dates are generated separately; they are separate measures and can differ.
- The region filter on the shipment pages uses the warehouse attached to the related order as a proxy, so it is not a true origin/destination-region filter.
- Route benchmark cost is modeled as quantity × benchmark freight per tonne, where benchmark freight per tonne is based on route distance. Actual freight contracting can include minimum charges, tolls, fuel adjustments, return loads, vehicle types, accessorial charges, and other factors not represented here.
- The savings slider is a scenario assumption, not a forecast or guaranteed saving.
- The recommendation rules are prompts for human investigation, not automated decisions.
- Do not present simulated numbers as results achieved at ITC or at any real employer.

## Suggested project demonstration

1. Start on Executive Overview and explain the KPIs.
2. Open Transportation and identify high-cost or underutilized shipment groups.
3. Open Warehouse & WSP and compare utilization, handling time, and cost variance.
4. Open Inventory Risk and explain stock cover and safety-stock flags.
5. Open Orders & Service and explain OTIF.
6. Finish on Recommendations and explain how each alert is calculated and what operational checks would be needed before acting.

## Repository structure

```text
.
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
├── data/
├── sql/
└── docs/
```

## License

Use this project as a learning and portfolio template. If you publish it, keep the synthetic-data disclaimer visible and ensure any changes you make are your own work and understood by you.
