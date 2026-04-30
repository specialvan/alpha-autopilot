from __future__ import annotations

from .common import clamp
from .schemas import NarrativeMarketState, NQMVector


class SellingPointContractGuard:
    def evaluate(self, market_state: NarrativeMarketState, vector: NQMVector) -> dict[str, object]:
        contract = market_state.project_state.selling_point_contract.strip()
        has_contract = bool(contract)
        a6 = vector.metrics.get("A6", 0.5)
        aligned = has_contract and a6 >= 0.45

        return {
            "has_contract": has_contract,
            "ip_flavor_alignment": clamp(a6),
            "aligned": aligned,
            "warning": "IP flavor drift risk" if has_contract and a6 < 0.45 else "",
        }
