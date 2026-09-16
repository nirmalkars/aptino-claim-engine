from typing import Any

from app.agents.base import add_trace


class ValidationAgent:
    name = "ValidationAgent"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        decision_analysis = state.get(
            "decision_analysis",
            {},
        )

        decision = decision_analysis.get(
            "decision",
            "NEEDS_REVIEW",
        )

        citations = decision_analysis.get(
            "citations",
            [],
        )

        unsupported_claims = []

        # Validate citation metadata
        for citation in citations:
            if not citation.get("chunk_id"):
                unsupported_claims.append(
                    "Citation is missing chunk ID."
                )

            if citation.get("page_number") is None:
                unsupported_claims.append(
                    f"Citation {citation.get('chunk_id')} "
                    "is missing page number."
                )

            if not citation.get("section"):
                unsupported_claims.append(
                    f"Citation {citation.get('chunk_id')} "
                    "is missing section."
                )

            if not citation.get("excerpt"):
                unsupported_claims.append(
                    f"Citation {citation.get('chunk_id')} "
                    "is missing excerpt."
                )

        # Every non-review decision must have policy citations
        if decision != "NEEDS_REVIEW" and not citations:
            unsupported_claims.append(
                f"{decision} decision requires policy citations."
            )

        # A rejection must have inspectable policy evidence
        if decision == "NOT_ADMISSIBLE" and not citations:
            unsupported_claims.append(
                "A NOT_ADMISSIBLE decision requires policy citations."
            )

        # If validation fails, downgrade the decision to NEEDS_REVIEW
        if unsupported_claims:
            decision_analysis["decision"] = "NEEDS_REVIEW"
            decision_analysis["confidence"] = min(
                float(decision_analysis.get("confidence", 0.0)),
                0.40,
            )

        state["decision_analysis"] = decision_analysis

        state["validation"] = {
            "status": "PASS" if not unsupported_claims else "FAIL",
            "unsupported_claims": unsupported_claims,
        }

        add_trace(
            state,
            self.name,
            "Validated decision citations and decision reliability",
            {
                "validation_status": state["validation"]["status"],
                "unsupported_claim_count": len(unsupported_claims),
                "final_decision": decision_analysis.get("decision"),
            },
        )

        return state