# Project walkthrough and interview preparation

## 90-second project explanation

"I built an independent Logistics and Warehouse Optimization Control Tower using simulated FMCG data. The objective was to connect logistics KPIs with operational decisions rather than only display charts. I used Python and Pandas to prepare shipment, warehouse, order and inventory data, wrote SQL queries for cost and service analysis, and created a Streamlit dashboard. The dashboard monitors freight spend, truck utilization, transporter performance, warehouse space and handling efficiency, inventory cover, safety-stock violations, and OTIF. It also flags potential issues using transparent rules and includes a scenario calculator for illustrative freight savings. The data and benchmarks are synthetic, so the project demonstrates my analytical approach rather than claiming actual company results."

## Questions you should be ready to answer

1. **Why did you choose this project?** It maps directly to transport, warehouse, inventory, cost control, service levels and process improvement responsibilities in logistics roles.
2. **What is truck utilization?** Loaded quantity divided by rated truck capacity, expressed as a percentage. Very low utilization may indicate consolidation opportunities, but delivery windows, product compatibility and route constraints must be checked.
3. **What is turnaround time?** The elapsed time a vehicle spends at a facility between arrival and departure. In a real operation, it should be split into gate, queue, dock, loading/unloading and documentation time.
4. **What is OTIF?** The share of eligible orders delivered both on time and in full.
5. **How do you calculate days of cover?** Available inventory divided by average daily demand.
6. **Why compare actual cost with a benchmark?** It helps prioritize investigation. It does not prove overspending unless the benchmark is comparable for distance, vehicle type, load, tolls, fuel, return trip and other commercial terms.
7. **How could you improve the data?** Use actual timestamps, route master data, contracted rate cards, SKU-level forecast error, batch/expiry data, loading dock schedules, vehicle types and warehouse shift data.
8. **What are the limitations?** Simulated data, simplified benchmark rates, separate shipment/order status generation, and rule-based recommendations that require human validation.
9. **How would you estimate savings?** Establish a validated baseline, define an operational intervention, estimate achievable changes, include implementation costs and service constraints, and measure actual before/after results.
10. **What would you do first in a real warehouse?** Validate the KPI definitions and source data, talk to operations teams, segment the problem by route/shift/SKU, confirm root causes, pilot a change, and track both cost and service outcomes.

## Interview honesty checklist

- State clearly that data is synthetic.
- Never say that you reduced real company costs by a specific percentage unless you measured that in a real project.
- Explain at least one SQL query and one Python transformation without reading the code line-by-line.
- Know the definitions and limitations of every KPI shown.
- Be ready to explain why a benchmark variance is only a signal for investigation.
