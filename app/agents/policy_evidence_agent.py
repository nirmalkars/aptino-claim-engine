from typing import Any

from app.agents.base import add_trace
from app.retrieval.hybrid import HybridRetriever
from app.services.evidence_service import format_evidence


class PolicyEvidenceAgent:
    name = "PolicyEvidenceAgent"

    def __init__(self):
        self.retriever = HybridRetriever()

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        claim = state["claim"]

        query_parts = [
            claim.get("task", ""),
            str(claim.get("patient", {})),
            str(claim.get("hospital", {})),
            str(claim.get("treatment", {})),
            str(claim.get("expenses_inr", {})),
        ]

        query = " ".join(
            part for part in query_parts if part
        )

        retrieved_results = self.retriever.search(
            query=query,
            dense_k=10,
            sparse_k=10,
            final_k=8,
        )

        evidence = format_evidence(retrieved_results)
        # print("DEBUG retrieved result:")
        # print(retrieved_results[0] if retrieved_results else None)

        # print("DEBUG formatted evidence:")
        # print(evidence[0] if evidence else None)

        state["retrieved_evidence"] = evidence

        add_trace(
            state,
            self.name,
            "Retrieved and formatted policy evidence",
            {
                "query": query,
                "retrieval_count": len(evidence),
                "citation_ready": True,
            },
        )

        return state