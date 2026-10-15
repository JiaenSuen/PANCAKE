# Instance Stratification — Formal TPPLIB Class-3 Study

This document freezes the structural descriptors used in the 100-instance canonical external study. The labels are computed from the imported `.tpp` files rather than assigned subjectively.

## Scale tiers

- **small:** `V <= 100` — 40 instances.
- **medium:** `150 <= V <= 200` — 40 instances.
- **large:** `V = 250` — 20 instances.

`V` includes the depot in the TPPLIB naming convention; the number of purchasable markets is `V-1`.

## Density descriptors

For each instance:

- `offers_per_product = offers_total / K`: average number of markets offering a product. This measures **product supply redundancy**.
- `offers_per_market = offers_total / (V-1)`: average number of products offered by a purchasable market. This measures **market assortment breadth**.
- `normalized_offer_density = offers_total / ((V-1)K)`: fraction of all market-product pairs that are available.
- `product_market_ratio = K/(V-1)`.
- `decision_scale = (V-1)K`: simple combinatorial size proxy used only as a structural covariate, not as a complexity theorem.

The two density measures are split into empirical tertiles over the 100 official instances:

- product-supply tertiles (`offers_per_product`): **51.6467**, **95.0200**;
- market-assortment tertiles (`offers_per_market`): **48.6827**, **75.3970**.

The resulting tier labels (`low`, `medium`, `high`) are stored directly in `instance_manifest.csv`, so every performance result can be traced to its structural class.

## Why both density axes are retained

They are not interchangeable. `offers_per_product` asks how many alternative suppliers exist for a typical product, while `offers_per_market` asks how broad a typical market's assortment is. The canonical analysis shows that DFOX is much more sensitive to **market assortment breadth** than ILS: high-assortment instances raise DFOX's median observed RPD by roughly 6.75 percentage points relative to the low-assortment tier, whereas the corresponding ILS shift is about 1.19 points. This distinction is therefore kept as a formal research variable rather than collapsing all density into one scalar.

## Statistical unit

The primary inferential unit is the **instance-level median over 10 paired seeds**, not the 3,000 individual runs. This prevents stochastic replications from being treated as independent benchmark instances.

## Files

- `instance_manifest.csv` — one row per instance with all descriptors and tier labels.
- `instance_stratification_summary.csv` — descriptor summaries by tier.
- `scale_by_market_assortment_counts.csv` and `scale_by_product_supply_counts.csv` — cross-tabulations.
- `VK_instance_counts.csv` — balanced V×K design counts.
