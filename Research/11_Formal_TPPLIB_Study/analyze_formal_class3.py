#!/usr/bin/env python3
"""Compatibility entry point for the reference-safe formal analysis.

The pre-audit analyzer assumed that every legacy baseline row was an exact optimum.
That implementation is preserved under legacy_scripts/ for provenance only.
"""
from pathlib import Path
import runpy

TARGET = Path(__file__).with_name("analyze_formal_class3_v2.py")
if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
