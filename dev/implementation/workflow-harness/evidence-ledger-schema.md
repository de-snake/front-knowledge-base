# Raw evidence ledger schema

Status: contract v1.

Purpose: make live/source facts reproducible without hardcoding any asset, oracle, or protocol. Every material claim that comes from RPC, explorer/API output, source code, docs, or a negative/no-result investigation should have a fact-level ledger entry that points to raw evidence and records how that evidence affected the workflow decision.

Canonical schema file: `dev/implementation/workflow-harness/contracts/evidence-ledger.schema.json`.

Regression fixture: `dev/implementation/workflow-harness/fixtures/evidence-ledger/positive-and-no-result/evidence-ledger.json`.

## Ledger location

Use one ledger per run or per stage artifact root. Preferred paths:

- Combined run root: `<run-root>/raw/evidence-ledger.json`.
- Asset scope: `<run-root>/asset-investment-diligence/tokens/<scope-slug>/raw/evidence-ledger.json`.
- Oracle scope: `<run-root>/oracle-analysis/tokens/<scope-slug>/raw/evidence-ledger.json`.
- Protocol adapter or run-level investigation: `<stage-artifact-dir>/raw/evidence-ledger.json`.

`raw_output_path` values are relative to the directory that contains the ledger. Large raw payloads stay in separate files; the ledger stores the path, normalized decoded value, and decision effect.

## Required fact envelope

Every fact entry must include:

| Field | Meaning |
| --- | --- |
| `fact_id` | Stable lowercase id for cross-references and validator findings. |
| `claim` | The exact claim the evidence supports, contradicts, or failed to find. |
| `scope_id` | Asset, oracle, PT market, protocol adapter, or run-level scope. |
| `stage_id` | Stage that gathered or consumed the fact. |
| `source_type` | `rpc`, `explorer`, `http_api`, `source_code`, `docs`, or `negative_search`. |
| `retrieved_at` | UTC timestamp when the evidence was fetched or the search was performed. |
| `method` | Retrieval method such as `eth_call`, `GET`, `code_search`, or `bounded docs search`. |
| `command_or_query` | Exact shell command, RPC payload, API query, search string, or structured method list. |
| `raw_output_path` | Repo-local path to the raw output, response, source snapshot, or search log. |
| `decoded_value` | Normalized value used by downstream analysis; use `null` only for no-result/unavailable facts and explain via `decision_effect`. |
| `status` | `confirmed`, `investigated_no_result`, `source_unavailable`, `source_inconclusive`, `contradicted`, `input_missing`, `not_investigated`, or `not_applicable`. |
| `freshness` | Object with `status` (`live`, `recent`, `stale`, `point_in_time`, `not_applicable`) and a plain-language basis. |
| `decision_effect` | Object with `effect` (`supports_decision`, `blocks_decision`, `requires_review`, `no_effect`) and rationale. |

## Type-specific evidence

### RPC facts

RPC facts must include `rpc`:

- `chain_id`;
- `block_number`;
- `contract`;
- `signature_or_selector`;
- `raw_output`;
- `decoder.decoder`;
- `decoder.abi_or_source`.

The raw output remains replayable through `raw_output_path`; the inline `rpc.raw_output` is a compact copy for quick review.

### Explorer and HTTP/API facts

Explorer/API facts must include `http_api`:

- `url`;
- `request.params` and `request.body` where relevant, with `null` when unused;
- `response_path`;
- `status_code`;
- `timestamp`.

Use `source_type: explorer` for explorer-specific APIs when explorer provenance matters; use `source_type: http_api` for ordinary REST/HTTP evidence.

### Source-code facts

Source-code facts must include repository, path, version/commit, and symbol or line range. Use this for decoded implementation facts, contract source findings, and codebase search hits that materially support a claim.

### Docs facts

Docs facts must include document URL/path, version/timestamp, and section/anchor. Use docs facts for public documentation claims, not for generated summaries of raw RPC/API output.

### Negative/no-result investigations

Any `source_type: negative_search` or `status: investigated_no_result` fact must include `negative_investigation`:

- `search_space` — the bounded universe being searched;
- `queries_or_methods_tried` — exact queries, commands, adapters, or methods;
- `sources_checked` — sources that were actually checked;
- `sufficiency_assessment.verdict` — `sufficient` or `insufficient`;
- `sufficiency_assessment.rationale` — why the search is deep enough for the stage, or why it remains inadequate.

A no-result fact is not a missing investigation. It is a positive statement that the declared search produced no result inside a bounded search space.

## Reuse by workflow stage

Asset stages use the same envelope for token identity, issuer controls, liquidity, oracle references, audits/incidents, and unavailable or inconclusive source facts.

Oracle stages use it for feed inventory RPC calls, source-primitive evidence, ABI/source decoding, docs-backed oracle policy, and no-result searches for missing route/market/feed adapters.

Protocol-specific adapters use it for adapter-specific route discovery, market existence, parameter reads, governance/config checks, and negative searches that prove an adapter-specific absence only inside an explicitly declared search space.

Parent synthesis should cite `fact_id` values instead of pasting raw outputs. Validators can later reject material claims that lack a ledger fact, lack raw output, or mark an unknown as no-result without the required search-space proof.
