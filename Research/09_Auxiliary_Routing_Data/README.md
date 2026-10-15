# Auxiliary routing-only upload audit

The user-supplied `user_uploaded_routing_dataset.zip` is preserved verbatim for provenance, but it is **not** treated as TPPLIB or as an official TPP benchmark.

Its two members are CSV routing datasets (`tsp_dataset.csv`, `tsp_instances_dataset.csv`) with city coordinates / distance matrices / route labels. They contain no TPPLIB `DEMAND_SECTION`, `OFFER_SECTION`, product demand, or market offer structure, so they cannot support TPP purchase-cost or official OPT-gap experiments.

Research use is intentionally limited to a future **routing-only isolation control**: it may help study whether an optimizer's weakness comes from pure tour search or from procurement-routing coupling. Until provenance and generation semantics are independently verified, results from this upload should not be reported as TSPLIB/TPPLIB benchmark results.

See `upload_audit.json` for SHA-256, member sizes and detected columns.
