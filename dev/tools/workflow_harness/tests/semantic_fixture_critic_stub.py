#!/usr/bin/env python3
"""Return a static semantic-critic fixture response after validating request shape."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: semantic_fixture_critic_stub.py RESPONSE_JSON REQUEST_JSON", file=sys.stderr)
        return 2
    response_path = Path(sys.argv[1])
    request_path = Path(sys.argv[-1])
    request = json.loads(request_path.read_text())
    if not request.get("output_artifacts"):
        print("semantic critic request has no output artifacts", file=sys.stderr)
        return 2
    if not request.get("validator_summary"):
        print("semantic critic request has no validator summary", file=sys.stderr)
        return 2
    print(response_path.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
