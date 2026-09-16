from typing import Any

from app.agents.base import add_trace


class CoverageExclusionAgent:
    name = "CoverageExclusionAgent"

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        claim = state["claim"]
        evidence = state.get("retrieved_evidence", [])

        task_text = str(claim.get("task", "")).lower()
        patient_text = str(claim.get("patient", {})).lower()
        treatment_text = str(claim.get("treatment", {})).lower()
        hospital_text = str(claim.get("hospital", {})).lower()
        document_text = str(claim.get("documents", [])).lower()

        claim_text = " ".join(
            [
                task_text,
                patient_text,
                treatment_text,
                hospital_text,
                document_text,
            ]
        )

        evidence_text = " ".join(
            item.get("text", "").lower()
            for item in evidence
        )

        combined_text = f"{claim_text} {evidence_text}"

        topics = {
            "pre_existing_disease": self._contains_any(
                claim_text,
                [
                    "pre-existing",
                    "pre existing",
                    "preexisting",
                    "existing disease",
                    "prior disease",
                    "previous illness",
                ],
            ),
            "maternity": self._contains_any(
                claim_text,
                [
                    "maternity",
                    "pregnancy",
                    "pregnant",
                    "delivery",
                    "childbirth",
                    "caesarean",
                    "c-section",
                ],
            ),
            "cosmetic_treatment": self._contains_any(
                claim_text,
                [
                    "cosmetic",
                    "plastic surgery",
                    "beautification",
                    "aesthetic surgery",
                ],
            ),
            "dental_treatment": self._contains_any(
                claim_text,
                [
                    "dental",
                    "tooth",
                    "teeth",
                    "dentist",
                ],
            ),
            "outpatient_treatment": self._contains_any(
                claim_text,
                [
                    "outpatient",
                    "out-patient",
                    "opd",
                    "without hospitalization",
                ],
            ),
        }

        waiting_period_relevant = (
            topics["pre_existing_disease"]
            or topics["maternity"]
        )

        exclusion_relevant = self._contains_any(
            combined_text,
            [
                "exclusion",
                "excluded",
                "not covered",
                "shall not be covered",
                "not admissible",
                "cosmetic treatment",
                "dental treatment",
                "outpatient treatment",
            ],
        )

        limit_relevant = self._contains_any(
            combined_text,
            [
                "subject to a limit",
                "sub-limit",
                "sub limit",
                "maximum",
                "limited to",
                "sum insured",
                "40% sum insured",
                "1.0% of the basic sum insured",
                "0.1% of the basic sum insured",
            ],
        )

        inpatient_indicator = self._contains_any(
            claim_text,
            [
                "inpatient",
                "in-patient",
                "hospitalization",
                "hospitalisation",
                "admitted",
                "discharged",
            ],
        )

        required_document_indicator = self._contains_any(
            document_text,
            [
                "discharge summary",
                "hospital bill",
                "medical report",
                "diagnostic report",
                "prescription",
                "invoice",
            ],
        )

        evidence_sufficient = len(evidence) > 0

        # Manual review is required when important eligibility conditions
        # cannot be established safely from the claim and policy evidence.
        requires_manual_review = (
            not evidence_sufficient
            or waiting_period_relevant
            or (
                inpatient_indicator
                and not required_document_indicator
            )
        )

        # These flags are deliberately conservative.
        # A topic alone is not enough to confirm an exclusion.
        exclusion_confirmed = False

        if topics["cosmetic_treatment"]:
            exclusion_confirmed = self._contains_any(
                evidence_text,
                [
                    "cosmetic treatment",
                    "cosmetic surgery",
                    "beautification",
                ],
            )

        if topics["dental_treatment"]:
            exclusion_confirmed = exclusion_confirmed or (
                "dental treatment" in evidence_text
                and (
                    "not covered" in evidence_text
                    or "excluded" in evidence_text
                    or "exclusion" in evidence_text
                )
            )

        if topics["outpatient_treatment"]:
            exclusion_confirmed = exclusion_confirmed or (
                "outpatient" in evidence_text
                and (
                    "not covered" in evidence_text
                    or "excluded" in evidence_text
                    or "exclusion" in evidence_text
                )
            )

        coverage_analysis = {
            "topics": topics,
            "waiting_period_relevant": waiting_period_relevant,
            "exclusion_relevant": exclusion_relevant,
            "exclusion_confirmed": exclusion_confirmed,
            "limit_relevant": limit_relevant,
            "inpatient_indicator": inpatient_indicator,
            "required_document_indicator": required_document_indicator,
            "evidence_sufficient": evidence_sufficient,
            "requires_manual_review": requires_manual_review,
        }

        state["coverage_analysis"] = coverage_analysis

        add_trace(
            state,
            self.name,
            "Analyzed coverage topics, exclusions, limits, and review conditions",
            {
                "topics": topics,
                "exclusion_relevant": exclusion_relevant,
                "exclusion_confirmed": exclusion_confirmed,
                "limit_relevant": limit_relevant,
                "requires_manual_review": requires_manual_review,
            },
        )

        return state

    @staticmethod
    def _contains_any(text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)