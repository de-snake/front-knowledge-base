#!/usr/bin/env python3
"""Protocol-specific investigation adapters for workflow-harness fact checks.

The workflow harness keeps protocol semantics here instead of baking Gearbox,
Morpho, or other protocol-specific names directly into packets or validators.
Adapters define the facts a worker must investigate, how to discover them, how
to prove a negative search, and when an absent market/route is a valid result.
Keep this module standard-library only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

FACT_STATES = (
    "found",
    "not_applicable",
    "input_missing",
    "not_investigated",
    "investigated_no_result",
    "source_unavailable",
    "source_inconclusive",
    "contradicted",
)

NO_RESULT_PROOF_CLASSES = (
    "registry_checked",
    "api_or_contract_query_attempted",
    "network_context_named",
    "evidence_path_present",
)


@dataclass(frozen=True)
class ProtocolFactSlot:
    fact_id: str
    label: str
    aliases: tuple[str, ...]
    discovery_methods: tuple[str, ...]
    negative_search_methods: tuple[str, ...] = ()
    no_result_semantics: str | None = None
    requires_no_result_proof: bool = False

    def to_packet_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Packet payloads are instructions for workers. Keep parser aliases out
        # of the human-facing packet and expose only the durable contract fields.
        data.pop("aliases", None)
        return data


@dataclass(frozen=True)
class ProtocolInvestigationAdapter:
    protocol: str
    adapter_id: str
    version: str
    purpose: str
    fact_result_states: tuple[str, ...]
    no_result_proof_classes: tuple[str, ...]
    required_facts: tuple[ProtocolFactSlot, ...]
    no_market_no_route_semantics: str

    def to_packet_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "adapter_id": self.adapter_id,
            "version": self.version,
            "purpose": self.purpose,
            "fact_result_states": list(self.fact_result_states),
            "no_result_proof_classes": list(self.no_result_proof_classes),
            "no_market_no_route_semantics": self.no_market_no_route_semantics,
            "required_facts": [fact.to_packet_dict() for fact in self.required_facts],
        }


GEARBOX_ORACLE_ADAPTER = ProtocolInvestigationAdapter(
    protocol="Gearbox",
    adapter_id="gearbox.oracle-market-parameter-context.v1",
    version="1.0.0",
    purpose=(
        "Require reusable Gearbox market, credit-manager, oracle, PFS, "
        "allowed-token, liquidation-threshold, and route investigation facts "
        "before an Analyze -> Propose workflow can treat a market or route as absent."
    ),
    fact_result_states=FACT_STATES,
    no_result_proof_classes=NO_RESULT_PROOF_CLASSES,
    no_market_no_route_semantics=(
        "A missing Gearbox market/credit manager or execution/liquidation route is "
        "valid only as state=investigated_no_result and only when the proof names "
        "the registry checked, API or contract query attempted, network/context, "
        "and a run-local evidence path. If the worker did not investigate, the "
        "state is not_investigated, never investigated_no_result."
    ),
    required_facts=(
        ProtocolFactSlot(
            fact_id="gearbox.market_or_credit_manager",
            label="Market or Credit Manager",
            aliases=("market or credit manager", "credit manager", "gearbox market"),
            discovery_methods=(
                "Check Gearbox market / Credit Manager registries for the asset and chain.",
                "Query configured protocol APIs or contracts when a registry does not resolve the fact.",
                "Record the chain/network and evidence artifact path for every positive or negative result.",
            ),
            negative_search_methods=(
                "Registry lookup by token and chain.",
                "Protocol API or on-chain contract query for supported market / Credit Manager entries.",
            ),
            no_result_semantics=(
                "No market is not an omission: record investigated_no_result only after registry, API/contract, "
                "network/context, and evidence-path proof."
            ),
            requires_no_result_proof=True,
        ),
        ProtocolFactSlot(
            fact_id="gearbox.oracle_feed",
            label="Oracle / main feed path",
            aliases=("main feed path", "oracle feed", "feed path"),
            discovery_methods=(
                "Resolve Gearbox oracle / price feed path for the market or Credit Manager context.",
                "Unwrap child/source primitives instead of stopping at a top-level label.",
            ),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.reserve_feed",
            label="Reserve feed path",
            aliases=("reserve feed path", "reserve feed"),
            discovery_methods=("Check whether an alternate/reserve feed exists for the resolved oracle context.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.safe_pricing_rule",
            label="Safe-pricing rule",
            aliases=("safe-pricing", "safe pricing"),
            discovery_methods=("Identify whether Gearbox applies conservative source selection or other safe-pricing rules.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.exit_health_factor",
            label="Exit Health Factor implication",
            aliases=("exit health factor",),
            discovery_methods=("Explain borrower exit-HF sensitivity for the feed / parameter context.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.liquidation_threshold",
            label="Liquidation Threshold",
            aliases=("liquidation threshold",),
            discovery_methods=(
                "Resolve LT/LTV-style protocol parameter context from the market, Credit Manager, or collateral config.",
                "Do not infer missing LT from generic token data."
            ),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.liquidation_threshold_ramp",
            label="Liquidation Threshold ramp",
            aliases=("lt ramp", "liquidation threshold ramp", "ramp"),
            discovery_methods=("Check whether LT is static, ramping, or governed by a scheduled parameter update.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.max_leverage",
            label="Max leverage implied by LT",
            aliases=("max leverage",),
            discovery_methods=("If LT is known, state the implied max leverage or mark the dependency unresolved.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.staleness_bounds_timestamp",
            label="Staleness, bounds, and timestamp controls",
            aliases=("staleness", "bounds", "timestamp"),
            discovery_methods=("Check stale-report, bound, and timestamp handling for the feed/source context.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.feed_swap_timelock",
            label="Feed swap / reserve / timelock status",
            aliases=("feed swap", "timelock"),
            discovery_methods=("Identify update authority, reserve path, feed swap path, and timelock/governance delay where available.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.delayed_withdrawal_branch",
            label="Delayed-withdrawal branch interaction",
            aliases=("delayed-withdrawal", "delayed withdrawal"),
            discovery_methods=("Check whether delayed withdrawals change the oracle or liquidation risk branch.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.allowed_token_status",
            label="Allowed-token / forbidden-token status",
            aliases=("allowed-token", "allowed token", "forbidden-token"),
            discovery_methods=(
                "Check allowed-token / forbidden-token collateral status for the market or Credit Manager context.",
                "Do not treat generic ERC-20 transferability as protocol allowlisting."
            ),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.issuer_controlled_branch",
            label="Issuer-controlled branch interaction",
            aliases=("issuer-controlled", "issuer controlled"),
            discovery_methods=("Check freeze, blacklist, reassignment, issuer-control, or RWA control branches where relevant.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.pfs_availability",
            label="PFS chain / token availability and update status",
            aliases=("pfs", "price feed store"),
            discovery_methods=("Check Price Feed Store chain/token availability and add/update status for the asset context.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.feed_update_authority",
            label="Instance Owner or feed-update authority",
            aliases=("instance owner", "feed-update authority", "feed update authority"),
            discovery_methods=("Identify Instance Owner, feed-update authority, or owner-controlled update path when available.",),
        ),
        ProtocolFactSlot(
            fact_id="gearbox.route_availability",
            label="Route / quote availability",
            aliases=("route", "swap route", "liquidation route", "execution route"),
            discovery_methods=(
                "Check route/quote availability for expected liquidation, unwind, or execution path on the named network.",
                "Preserve router/API/contract evidence for every route result."
            ),
            negative_search_methods=(
                "Query route/quote APIs or contracts for the asset/network context.",
                "Check protocol-specific route registries or allowed-router configuration when available.",
            ),
            no_result_semantics=(
                "No route is valid only as investigated_no_result with route registry/API/contract, network/context, and evidence-path proof."
            ),
            requires_no_result_proof=True,
        ),
    ),
)

ADAPTERS_BY_PROTOCOL = {
    GEARBOX_ORACLE_ADAPTER.protocol.lower(): GEARBOX_ORACLE_ADAPTER,
}


def get_protocol_adapter(protocol: Any) -> ProtocolInvestigationAdapter | None:
    """Return the adapter for a protocol string, if one exists."""
    key = str(protocol or "").strip().lower()
    return ADAPTERS_BY_PROTOCOL.get(key)


def packet_payload_for_protocol(protocol: Any) -> dict[str, Any] | None:
    adapter = get_protocol_adapter(protocol)
    return adapter.to_packet_dict() if adapter else None
