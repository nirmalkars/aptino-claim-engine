from typing import Any

from app.agents.base import add_trace


class CaseAnalysisAgent:
    name = "CaseAnalysisAgent"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        claim = state["claim"]

        missing_fields = []
        investigation_plan = []

        if not claim.get("policy_start_date"):
            missing_fields.append("policy_start_date")

        if not claim.get("claim_date"):
            missing_fields.append("claim_date")

        if not claim.get("patient"):
            missing_fields.append("patient information")

        if not claim.get("hospital"):
            missing_fields.append("hospital information")

        if not claim.get("treatment"):
            missing_fields.append("treatment information")

        if not claim.get("documents"):
            missing_fields.append("supporting documents")

        investigation_plan.extend(
            [
                "Check policy eligibility and coverage period",
                "Check waiting-period provisions",
                "Check exclusions and limitations",
                "Check treatment and expense admissibility",
                "Check whether supporting evidence is sufficient",
            ]
        )

        state["missing_fields"] = missing_fields
        state["investigation_plan"] = investigation_plan

        state["case_analysis"] = {
            "case_id": claim.get("case_id"),
            "policy_id": claim.get("policy_id"),
            "missing_fields": missing_fields,
            "investigation_plan": investigation_plan,
        }

        add_trace(
            state,
            self.name,
            "Analyzed claim structure",
            {
                "missing_field_count": len(missing_fields),
                "plan_step_count": len(investigation_plan),
            },
        )

        return state