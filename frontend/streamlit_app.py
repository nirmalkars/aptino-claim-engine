import json
from typing import Any

import requests
import streamlit as st


# API_URL = "http://127.0.0.1:8000"
import os

API_URL = st.secrets.get(
    "API_URL",
    os.getenv("API_URL", "http://127.0.0.1:8000")
).rstrip("/")

st.write("Backend URL:", API_URL)

st.set_page_config(
    page_title="Policy-Aware Claim Decision Engine",
    page_icon="📄",
    layout="wide",
)


st.title("Policy-Aware Multi-Agent RAG Claim Decision Engine")

st.write(
    "Submit a health insurance claim case and inspect the "
    "policy-grounded multi-agent analysis."
)


def load_test_cases() -> list[dict[str, Any]]:
    with open(
        "data/public_test_cases.json",
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if isinstance(data, dict):
        return data.get("cases", [])

    return data


def display_decision(result: dict[str, Any]) -> None:
    decision = result.get("decision", "NEEDS_REVIEW")
    confidence = result.get("confidence", 0.0)

    st.subheader("Decision")

    if decision == "ADMISSIBLE":
        st.success(decision)
    elif decision == "ADMISSIBLE_WITH_LIMITS":
        st.warning(decision)
    elif decision == "PARTIALLY_ADMISSIBLE":
        st.warning(decision)
    elif decision == "NOT_ADMISSIBLE":
        st.error(decision)
    else:
        st.info(decision)

    st.metric(
        label="Confidence",
        value=f"{confidence:.2%}",
    )

    st.subheader("Key Findings")

    findings = result.get("key_findings", [])

    if findings:
        for finding in findings:
            st.write(f"- {finding}")
    else:
        st.write("No findings returned.")

    st.subheader("Applicable Limits")

    limits = result.get("applicable_limits", [])

    if limits:
        for limit in limits:
            st.write(f"- {limit}")
    else:
        st.write("No applicable limits identified.")

    st.subheader("Missing Evidence")

    missing_evidence = result.get("missing_evidence", [])

    if missing_evidence:
        for item in missing_evidence:
            st.write(f"- {item}")
    else:
        st.write("No missing evidence reported.")


def display_citations(result: dict[str, Any]) -> None:
    st.subheader("Policy Citations")

    citations = result.get("citations", [])

    if not citations:
        st.warning("No policy citations were returned.")
        return

    for index, citation in enumerate(result.get("citations", []), start=1):
        st.markdown(f"### Citation {index}: {citation.get('chunk_id', 'Unknown')}")

        st.markdown(
            f"**Source:** {citation.get('source', 'Unknown')}"
        )

        st.markdown(
            f"**Page:** {citation.get('page_number', 'Unknown')}"
        )

        st.markdown(
            f"**Section:** {citation.get('section', 'Unknown')}"
        )

        st.markdown(
            f"**Excerpt:** {citation.get('excerpt', 'Unknown')}"
        )


def display_validation(result: dict[str, Any]) -> None:
    st.subheader("Validation")

    validation = result.get("validation", {})
    status = validation.get("status", "FAIL")

    if status == "PASS":
        st.success("Validation passed")
    else:
        st.error("Validation failed")

    unsupported_claims = validation.get(
        "unsupported_claims",
        [],
    )

    for claim in unsupported_claims:
        st.write(f"- {claim}")


def display_trace(result: dict[str, Any]) -> None:
    st.subheader("Agent Trace")

    trace = result.get("trace", [])

    if not trace:
        st.write("No trace available.")
        return

    for index, item in enumerate(trace, start=1):
        agent = item.get("agent", "Unknown agent")
        action = item.get("action", "Unknown action")
        details = item.get("details", {})

        with st.expander(f"{index}. {agent}"):
            st.write(f"**Action:** {action}")
            st.json(details)


test_cases = load_test_cases()

case_options = [
    case.get("case_id", f"case-{index}")
    for index, case in enumerate(test_cases)
]

selected_case_id = st.selectbox(
    "Select a supplied test case",
    options=case_options,
)

selected_case = next(
    case
    for case in test_cases
    if case.get("case_id") == selected_case_id
)

st.subheader("Claim Input")

st.json(selected_case)

if st.button("Analyze Claim", type="primary"):
    try:
        with st.spinner("Running multi-agent claim analysis..."):
            response = requests.post(
                f"{API_URL}/analyze",
                json=selected_case,
                timeout=180,
            )

        if response.status_code == 200:
            result = response.json()

            st.success("Claim analysis completed.")

            display_decision(result)
            display_citations(result)
            display_validation(result)
            display_trace(result)

        else:
            st.error(
                f"API request failed: {response.status_code}"
            )
            st.code(response.text)

    except requests.exceptions.RequestException as exc:
        st.error(
            "Could not connect to the FastAPI server. "
            "Make sure the API is running."
        )
        st.exception(exc)
