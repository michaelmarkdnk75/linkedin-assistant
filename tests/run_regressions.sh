#!/bin/sh
# Run all regression tests (setup/regressions.md). Exit 0 = every past fix still locked. Read-only, no network, no LinkedIn calls.
cd "$(dirname "$0")/.." && python3 -I -W ignore tests/test_regressions.py
