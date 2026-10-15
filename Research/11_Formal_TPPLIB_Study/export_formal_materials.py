#!/usr/bin/env python3
"""Deprecated pre-audit exporter guard.

Paper-facing tables/figures are now generated from reference-safe outputs under
Research/07_Paper_Materials/formal_tables and the formal-study `formal_*` figures.
The historical exporter is retained under legacy_scripts/ because it used the
superseded assumption that all imported baseline rows were exact optima.
"""
if __name__ == "__main__":
    raise SystemExit(
        "Deprecated: do not regenerate manuscript materials with the pre-audit exact-OPT semantics. "
        "Use analyze_formal_class3_v2.py and the reference-safe paper tables instead."
    )
