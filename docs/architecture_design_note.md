# Architecture and Design Note

## 1. Project Overview

The Policy-Aware Multi-Agent RAG Claim Decision Engine analyzes insurance claim cases against an authoritative policy document.

The system retrieves relevant policy evidence, analyzes claim information, evaluates coverage conditions, generates a structured decision, and validates the decision using policy citations.

The system is designed as a decision-support tool. It does not replace human insurance claim adjudication.

---

## 2. High-Level Architecture

The system contains the following major components:

1. Policy ingestion
2. Hybrid retrieval
3. Multi-agent workflow
4. Decision generation
5. Citation validation
6. FastAPI backend
7. Streamlit frontend
8. Evaluation pipeline

The policy PDF is processed into page-aware and section-aware chunks. These chunks are indexed for both dense and sparse retrieval.

For each claim, the system retrieves relevant policy evidence and passes the evidence through specialized agents.

---

## 3. Agent Boundaries

### Case Analysis Agent

The Case Analysis Agent extracts structured information from the claim.

Responsibilities include:

- Identifying patient and hospital details.
- Extracting treatment information.
- Identifying dates and claimed amounts.
- Checking available documents.
- Identifying missing claim information.

This agent focuses on claim understanding and does not make the final policy decision.

### Policy Evidence Agent

The Policy Evidence Agent retrieves relevant policy sections.

Responsibilities include:

- Creating a retrieval query from the claim.
- Running dense retrieval.
- Running sparse BM25 retrieval.
- Combining retrieval results.
- Returning policy chunks with metadata.

This agent focuses on finding evidence rather than interpreting the final decision.

### Coverage Agent

The Coverage Agent analyzes retrieved evidence for coverage-related conditions.

Responsibilities include:

- Identifying coverage clauses.
- Identifying exclusions.
- Checking waiting periods.
- Identifying limits and sub-limits.
- Detecting manual-review requirements.

### Decision Agent

The Decision Agent combines the claim analysis, coverage analysis, and policy evidence.

It generates:

- Decision status.
- Confidence score.
- Findings.
- Coverage limitations.
- Missing evidence.
- Policy citations.

The supported decision statuses are:

- ADMISSIBLE
- ADMISSIBLE_WITH_LIMITS
- PARTIALLY_ADMISSIBLE
- NOT_ADMISSIBLE
- NEEDS_REVIEW

### Validation Agent

The Validation Agent checks whether the generated decision is supported by valid evidence.

It verifies:

- Citation presence.
- Chunk IDs.
- Page numbers.
- Policy sections.
- Evidence excerpts.
- Decision support.

If the evidence is insufficient, the final decision is changed to NEEDS_REVIEW.

---

## 4. State Flow

The workflow uses a shared state object.

The state contains information such as:

- Original claim.
- Case analysis.
- Retrieved evidence.
- Coverage analysis.
- Decision analysis.
- Validation result.
- Agent trace.

The state flows through the agents in the following order:

```text
Claim Input
    |
    v
Case Analysis Agent
    |
    v
Policy Evidence Agent
    |
    v
Coverage Agent
    |
    v
Decision Agent
    |
    v
Validation Agent
    |
    v
Final Structured Result