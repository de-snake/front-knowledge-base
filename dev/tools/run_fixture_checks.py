#!/usr/bin/env python3
"""Convenience wrapper for the workflow-harness smoke checks."""

from __future__ import annotations

import runpy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKS = REPO_ROOT / "dev/tools/workflow_harness/tests/run_fixture_checks.py"

if __name__ == "__main__":
    runpy.run_path(str(CHECKS), run_name="__main__")
