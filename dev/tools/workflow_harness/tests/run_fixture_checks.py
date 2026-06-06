#!/usr/bin/env python3
"""Smoke-run the workflow-harness regression checks without pytest."""

from __future__ import annotations

import importlib.util
import inspect
import subprocess
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
TEST_DIR = Path(__file__).resolve().parent


def run_pytest_style_module(label: str, path: Path) -> int:
    print(f"== {label} ==")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        print(f"failed to load {path}")
        return 2
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    failures = 0
    total = 0
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        fn = getattr(module, name)
        if not callable(fn):
            continue
        total += 1
        setup = getattr(module, "setup_function", None)
        teardown = getattr(module, "teardown_function", None)
        try:
            if callable(setup):
                if len(inspect.signature(setup).parameters) == 0:
                    setup()
                else:
                    setup(fn)
            fn()
            print(f"PASS {name}")
        except Exception:  # noqa: BLE001 - report every smoke failure.
            failures += 1
            print(f"FAIL {name}")
            traceback.print_exc()
        finally:
            if callable(teardown):
                try:
                    if len(inspect.signature(teardown).parameters) == 0:
                        teardown()
                    else:
                        teardown(fn)
                except Exception:  # noqa: BLE001 - report teardown failures.
                    failures += 1
                    print(f"FAIL teardown for {name}")
                    traceback.print_exc()
    print(f"{label}: ran {total}, failures {failures}")
    return 0 if failures == 0 and total > 0 else 2


def run_command(label: str, cmd: list[str]) -> int:
    print(f"== {label} ==")
    proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True)
    print(f"{label}: exit {proc.returncode}")
    return proc.returncode


def main() -> int:
    checks = [
        ("fixture matrix", lambda: run_pytest_style_module("fixture matrix", TEST_DIR / "test_fixtures.py")),
        ("evidence ledger schema", lambda: run_pytest_style_module("evidence ledger schema", TEST_DIR / "test_evidence_ledger_schema.py")),
        ("semantic critic runner", lambda: run_pytest_style_module("semantic critic runner", TEST_DIR / "test_semantic_critic_runner.py")),
        ("regression eval suite", lambda: run_pytest_style_module("regression eval suite", TEST_DIR / "test_regression_eval_suite.py")),
        ("workflow entrypoint", lambda: run_command("workflow entrypoint", ["python3", "-m", "unittest", "dev.tools.workflow_harness.tests.test_workflow_entrypoint"])),
    ]
    failures = 0
    for _label, fn in checks:
        rc = fn()
        if rc != 0:
            failures += 1
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
