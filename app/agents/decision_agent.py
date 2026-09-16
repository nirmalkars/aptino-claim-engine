from typing import Any

from app.agents.base import add_trace


class DecisionAgent:
    name = "DecisionAgent"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        missing_fields = state.get("missing_fields", [])
        evidence = state.get("retrieved_evidence", [])
        coverage = state.get("coverage_analysis", {})

        citations = self._build_citations(evidence)

        findings: list[str] = []
        applicable_limits: list[str] = []
        missing_evidence = list(missing_fields)

        topics = coverage.get("topics", {})

        if missing_fields:
            decision = "NEEDS_REVIEW"
            confidence = 0.35

            findings.append(
                "Required claim information is missing."
            )

        elif not evidence:
            decision = "NEEDS_REVIEW"
            confidence = 0.20

            findings.append(
                "No relevant policy evidence was retrieved."
            )

            missing_evidence.append(
                "Relevant policy evidence"
            )

        elif coverage.get("exclusion_confirmed"):
            decision = "NOT_ADMISSIBLE"
            confidence = 0.75

            findings.append(
                "Retrieved policy evidence indicates that the "
                "treatment may fall under an applicable exclusion."
            )

        elif coverage.get("waiting_period_relevant"):
            decision = "NEEDS_REVIEW"
            confidence = 0.45

            findings.append(
                "The claim may involve a waiting-period condition."
            )

            missing_evidence.append(
                "Confirmation of policy commencement date, "
                "continuous coverage, and waiting-period eligibility"
            )

        elif coverage.get("requires_manual_review"):
            decision = "NEEDS_REVIEW"
            confidence = 0.50

            findings.append(
                "Additional claim documents or eligibility details "
                "are required for a reliable decision."
            )

        elif coverage.get("limit_relevant"):
            decision = "ADMISSIBLE_WITH_LIMITS"
            confidence = 0.65

            findings.append(
                "The claim appears potentially admissible, subject "
                "to applicable policy limits or sub-limits."
            )

            applicable_limits.append(
                "Review the applicable policy limits or sub-limits "
                "before determining the payable amount."
            )

        else:
            decision = "ADMISSIBLE"
            confidence = 0.60

            findings.append(
                "The available claim information and retrieved "
                "policy evidence do not indicate an identified "
                "exclusion or unresolved waiting-period issue."
            )

        if topics.get("pre_existing_disease"):
            findings.append(
                "The claim may involve a pre-existing disease."
            )

        if topics.get("maternity"):
            findings.append(
                "The claim may involve maternity-related treatment."
            )

        if topics.get("cosmetic_treatment"):
            findings.append(
                "The claim may involve cosmetic treatment."
            )

        if topics.get("dental_treatment"):
            findings.append(
                "The claim may involve dental treatment."
            )

        if topics.get("outpatient_treatment"):
            findings.append(
                "The claim may involve outpatient treatment."
            )

        if coverage.get("limit_relevant") and not applicable_limits:
            applicable_limits.append(
                "Review applicable policy limits or sub-limits."
            )

        if coverage.get("exclusion_relevant"):
            findings.append(
                "Potential exclusion-related policy language was "
                "identified in the retrieved evidence."
            )

        missing_evidence = list(dict.fromkeys(missing_evidence))

        state["decision_analysis"] = {
            "decision": decision,
            "confidence": confidence,
            "key_findings": findings,
            "applicable_limits": applicable_limits,
            "missing_evidence": missing_evidence,
            "citations": citations,
        }

        add_trace(
            state,
            self.name,
            "Generated evidence-aware preliminary decision",
            {
                "decision": decision,
                "confidence": confidence,
                "citation_count": len(citations),
                "missing_evidence_count": len(missing_evidence),
            },
        )

        return state

    @staticmethod
    def _build_citations(
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        citations = []

        for item in evidence:
            citations.append(
                {
                    "chunk_id": item.get("chunk_id"),
                    "page_number": item.get("page_number"),
                    "section": item.get("section"),
                    "source": item.get("source", "policy.pdf"),
                    "excerpt": item.get("text", ""),
                    # "excerpt": item.get("text", "")[:500],
                }
            )

        return citations