from typing import Any

from app.schemas.decision import ClaimDecision


def build_claim_decision(state: dict[str, Any]) -> ClaimDecision:
    decision_analysis = state.get("decision_analysis", {})

    print("DEBUG decision_analysis:")
    print(decision_analysis)

    print("DEBUG decision citations:")
    print(decision_analysis.get("citations", []))

    validation = state.get(
        "validation",
        {
            "status": "FAIL",
            "unsupported_claims": [
                "Validation result was not generated."
            ],
        },
    )

    return ClaimDecision(
        case_id=state["case_id"],
        decision=decision_analysis.get(
            "decision",
            "NEEDS_REVIEW",
        ),
        confidence=decision_analysis.get(
            "confidence",
            0.0,
        ),
        key_findings=decision_analysis.get(
            "key_findings",
            [],
        ),
        applicable_limits=decision_analysis.get(
            "applicable_limits",
            [],
        ),
        missing_evidence=decision_analysis.get(
            "missing_evidence",
            state.get("missing_fields", []),
        ),
        citations=decision_analysis.get(
            "citations",
            [],
        ),
        validation=validation,
        trace=state.get("trace", []),
    )