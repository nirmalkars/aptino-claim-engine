import sys
import json
from pathlib import Path
from typing import Any


# ---------------------------------------------------------
# Project path configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.schemas.claim import ClaimCase
from app.workflow.claim_workflow import ClaimWorkflow


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

PUBLIC_CASES_PATH = DATA_DIR / "public_test_cases.json"
ADDITIONAL_CASES_PATH = DATA_DIR / "additional_test_cases.json"

EVALUATION_DIR = PROJECT_ROOT / "evaluation"

if not EVALUATION_DIR.exists():
    EVALUATION_DIR = PROJECT_ROOT / "evalution"

OUTPUT_PATH = EVALUATION_DIR / "evaluation_results.json"


# ---------------------------------------------------------
# Load cases
# ---------------------------------------------------------

def load_cases(file_path: Path) -> list[dict[str, Any]]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Test case file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        cases = data.get("cases", [])
    elif isinstance(data, list):
        cases = data
    else:
        raise ValueError(
            f"Unsupported JSON format in {file_path}"
        )

    if not isinstance(cases, list):
        raise ValueError(
            f"'cases' must be a list in {file_path}"
        )

    return cases


def load_all_test_cases() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    public_cases = load_cases(PUBLIC_CASES_PATH)
    additional_cases = load_cases(ADDITIONAL_CASES_PATH)

    all_cases = public_cases + additional_cases

    return public_cases, additional_cases, all_cases


# ---------------------------------------------------------
# Evaluate one case
# ---------------------------------------------------------

def evaluate_case(
    workflow: ClaimWorkflow,
    raw_case: dict[str, Any],
    case_source: str,
) -> dict[str, Any]:

    claim = ClaimCase.model_validate(raw_case)

    result = workflow.run(claim.model_dump())

    decision_analysis = result.get(
        "decision_analysis",
        {},
    )

    validation = result.get(
        "validation",
        {},
    )

    retrieved_evidence = result.get(
        "retrieved_evidence",
        [],
    )

    citations = decision_analysis.get(
        "citations",
        [],
    )

    valid_page_citations = sum(
        1
        for citation in citations
        if citation.get("page_number") is not None
        and citation.get("page_number") != "Unknown"
    )

    return {
        "case_id": claim.case_id,
        "source": case_source,
        "decision": decision_analysis.get(
            "decision",
            "NEEDS_REVIEW",
        ),
        "confidence": decision_analysis.get(
            "confidence",
            0.0,
        ),
        "citation_count": len(citations),
        "valid_page_citation_count": valid_page_citations,
        "retrieval_count": len(retrieved_evidence),
        "validation_status": validation.get(
            "status",
            "FAIL",
        ),
        "missing_evidence": decision_analysis.get(
            "missing_evidence",
            [],
        ),
    }


# ---------------------------------------------------------
# Calculate metrics
# ---------------------------------------------------------

def calculate_summary(
    results: list[dict[str, Any]],
) -> dict[str, Any]:

    total_cases = len(results)

    decision_counts: dict[str, int] = {}

    for result in results:
        decision = result.get(
            "decision",
            "ERROR",
        )

        decision_counts[decision] = (
            decision_counts.get(decision, 0) + 1
        )

    cases_with_retrieval = sum(
        1
        for result in results
        if result.get("retrieval_count", 0) > 0
    )

    cases_with_citations = sum(
        1
        for result in results
        if result.get("citation_count", 0) > 0
    )

    cases_with_valid_page_citations = sum(
        1
        for result in results
        if result.get("valid_page_citation_count", 0) > 0
    )

    passed_validation = sum(
        1
        for result in results
        if result.get("validation_status") == "PASS"
    )

    needs_review_cases = sum(
        1
        for result in results
        if result.get("decision") == "NEEDS_REVIEW"
    )

    error_cases = sum(
        1
        for result in results
        if result.get("decision") == "ERROR"
    )

    total_retrieved_chunks = sum(
        result.get("retrieval_count", 0)
        for result in results
    )

    total_citations = sum(
        result.get("citation_count", 0)
        for result in results
    )

    average_confidence = (
        sum(
            result.get("confidence", 0.0)
            for result in results
        )
        / total_cases
        if total_cases
        else 0.0
    )

    return {
        "total_cases": total_cases,
        "decision_counts": decision_counts,
        "needs_review_cases": needs_review_cases,
        "error_cases": error_cases,

        "cases_with_retrieval": cases_with_retrieval,
        "retrieval_coverage": (
            cases_with_retrieval / total_cases
            if total_cases
            else 0.0
        ),

        "cases_with_citations": cases_with_citations,
        "citation_coverage": (
            cases_with_citations / total_cases
            if total_cases
            else 0.0
        ),

        "cases_with_valid_page_citations": (
            cases_with_valid_page_citations
        ),
        "page_citation_coverage": (
            cases_with_valid_page_citations / total_cases
            if total_cases
            else 0.0
        ),

        "total_retrieved_chunks": total_retrieved_chunks,
        "average_retrieved_chunks_per_case": (
            round(
                total_retrieved_chunks / total_cases,
                4,
            )
            if total_cases
            else 0.0
        ),

        "total_citations": total_citations,
        "average_citations_per_case": (
            round(
                total_citations / total_cases,
                4,
            )
            if total_cases
            else 0.0
        ),

        "passed_validation": passed_validation,
        "validation_pass_rate": (
            passed_validation / total_cases
            if total_cases
            else 0.0
        ),

        "average_confidence": round(
            average_confidence,
            4,
        ),
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:

    print("Loading test cases...")

    public_cases, additional_cases, all_cases = (
        load_all_test_cases()
    )

    print(
        f"Public cases loaded: {len(public_cases)}"
    )

    print(
        f"Additional cases loaded: {len(additional_cases)}"
    )

    print(
        f"Total cases to evaluate: {len(all_cases)}"
    )

    workflow = ClaimWorkflow()

    public_case_ids = {
        case.get("case_id")
        for case in public_cases
    }

    results: list[dict[str, Any]] = []

    for index, raw_case in enumerate(
        all_cases,
        start=1,
    ):

        case_id = raw_case.get(
            "case_id",
            f"unknown-{index}",
        )

        case_source = (
            "public"
            if case_id in public_case_ids
            else "additional"
        )

        print(
            f"Evaluating case "
            f"{index}/{len(all_cases)}: "
            f"{case_id}"
        )

        try:
            result = evaluate_case(
                workflow=workflow,
                raw_case=raw_case,
                case_source=case_source,
            )

            results.append(result)

        except Exception as exc:

            print(
                f"Error while evaluating "
                f"{case_id}: {exc}"
            )

            results.append(
                {
                    "case_id": case_id,
                    "source": case_source,
                    "decision": "ERROR",
                    "confidence": 0.0,
                    "citation_count": 0,
                    "valid_page_citation_count": 0,
                    "retrieval_count": 0,
                    "validation_status": "FAIL",
                    "missing_evidence": [
                        str(exc)
                    ],
                }
            )

    public_results = [
        result
        for result in results
        if result["source"] == "public"
    ]

    additional_results = [
        result
        for result in results
        if result["source"] == "additional"
    ]

    output = {
        "metadata": {
            "public_case_count": len(public_cases),
            "additional_case_count": len(additional_cases),
            "total_case_count": len(all_cases),
        },
        "summary": calculate_summary(results),
        "public_summary": calculate_summary(public_results),
        "additional_summary": calculate_summary(
            additional_results
        ),
        "results": results,
    }

    EVALUATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\nEvaluation completed.")

    print("\nOverall summary:")
    print(
        json.dumps(
            output["summary"],
            indent=2,
        )
    )

    print("\nPublic summary:")
    print(
        json.dumps(
            output["public_summary"],
            indent=2,
        )
    )

    print("\nAdditional summary:")
    print(
        json.dumps(
            output["additional_summary"],
            indent=2,
        )
    )

    print(
        f"\nResults saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()