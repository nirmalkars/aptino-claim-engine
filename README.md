# Policy-Aware Multi-Agent RAG Claim Decision Engine

A policy-aware insurance claim analysis system that combines hybrid retrieval, policy evidence extraction, multi-agent orchestration, rule-based decision analysis, citation validation, and a FastAPI/Streamlit interface.

The system analyzes claim cases against an authoritative policy document and produces a structured decision with supporting policy citations.

## Features

- PDF policy ingestion
- Page-aware and section-aware document chunking
- Dense vector retrieval using SentenceTransformers and FAISS
- Sparse retrieval using BM25
- Reciprocal Rank Fusion for hybrid retrieval
- Cross-encoder reranking
- Multi-agent claim analysis workflow
- Structured claim and decision schemas using Pydantic
- Evidence-based policy citations
- Citation and page-number validation
- Conservative `NEEDS_REVIEW` fallback
- FastAPI REST API
- Streamlit user interface
- Evaluation on public and additional test cases
- Failure analysis documentation

## System Architecture

```text
Policy PDF
    |
    v
PDF Ingestion -> Page Extraction -> Document Chunking
    |
    v
Policy Chunks + Page Metadata + Section Metadata + Chunk IDs
    |
    +----------------------+----------------------+
    v                      v                      
Dense Retrieval       Sparse Retrieval
SentenceTransformers  BM25
FAISS                  
    |                      |
    +----------+-----------+
               v
    Reciprocal Rank Fusion
               |
               v
       Cross-Encoder Reranking
               |
               v
       Multi-Agent Workflow
               |
     +---------+---------+
     v         v         v
Case       Policy     Coverage
Analysis   Evidence   Agent
Agent      Agent
     +---------+---------+
               v
         Decision Agent
               |
               v
        Validation Agent
               |
               v
          Final Decision
          - Findings
          - Limits
          - Missing Evidence
          - Policy Citations
          - Validation Result
```

## Multi-Agent Workflow

The system uses multiple specialized agents.

### 1. Case Analysis Agent

The Case Analysis Agent extracts and structures important information from the claim.

It identifies:

- Patient information
- Hospital information
- Treatment details
- Admission and discharge dates
- Claimed amount
- Policy information
- Submitted documents
- Missing claim information
- Potential review requirements

The output is stored in the shared workflow state for use by the other agents.

### 2. Policy Evidence Agent

The Policy Evidence Agent retrieves relevant sections from the authoritative policy document.

The retrieval pipeline combines:

- Dense semantic retrieval using SentenceTransformers
- FAISS vector similarity search
- Sparse keyword retrieval using BM25
- Reciprocal Rank Fusion
- Cross-encoder reranking
- Page and section metadata

The agent returns policy evidence with chunk IDs, page numbers, sections, source names, and text excerpts.

### 3. Coverage Agent

The Coverage Agent analyzes the retrieved policy evidence for relevant coverage conditions.

It checks for:

- Coverage clauses
- Exclusions
- Waiting periods
- Coverage limits
- Sub-limits
- Special conditions
- Manual review requirements

The agent does not apply an exclusion unless the available evidence supports it.

### 4. Decision Agent

The Decision Agent combines the claim analysis, policy evidence, and coverage analysis to generate a structured decision.

The supported decision statuses are:

- `ADMISSIBLE`
- `ADMISSIBLE_WITH_LIMITS`
- `PARTIALLY_ADMISSIBLE`
- `NOT_ADMISSIBLE`
- `NEEDS_REVIEW`

The decision includes:

- Final decision status
- Confidence score
- Findings
- Coverage limitations
- Missing evidence
- Policy citations
- Explanation of the decision

If the available evidence is insufficient, the system returns `NEEDS_REVIEW` instead of making an unsupported decision.

### 5. Validation Agent

The Validation Agent checks the quality and supportability of the generated decision.

It validates:

- Presence of citations
- Citation chunk IDs
- Page numbers
- Policy sections
- Source document
- Evidence excerpts
- Decision support
- Missing evidence
- Validation status

If a decision cannot be supported by valid policy evidence, it is downgraded to `NEEDS_REVIEW`.

## Project Structure

```text
aptino-claim-engine/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── claim.py
│   │   └── decision.py
│   ├── services/
│   │   ├── decision_service.py
│   │   ├── evidence_service.py
│   │   └── policy_rules.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── dense.py
│   │   ├── sparse.py
│   │   ├── fusion.py
│   │   ├── reranker.py
│   │   └── hybrid.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── base.py
│   │   ├── case_analysis_agent.py
│   │   ├── policy_evidence_agent.py
│   │   ├── coverage_agent.py
│   │   ├── decision_agent.py
│   │   └── validation_agent.py
│   └── workflow/
│       ├── __init__.py
│       └── claim_workflow.py
├── data/
│   ├── policy.pdf
│   ├── public_test_cases.json
│   ├── additional_test_cases.json
│   └── processed/
│       └── policy_chunks.json
├── evalution/
│   ├── __init__.py
│   ├── evaluate.py
│   ├── evaluation_results.json
│   └── failure_analysis.md
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── ingest_policy.py
│   ├── test_retrieval.py
│   ├── test_schemas.py
│   └── test_workflow.py
├── requirements.txt
└── README.md
```

## Installation

This project uses Python 3.10 or later.

### Create a virtual environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux or macOS

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Policy Ingestion

Run the policy ingestion script:

```bash
python scripts/ingest_policy.py
```

The ingestion pipeline:

1. Reads the policy PDF.
2. Extracts text page by page.
3. Splits the text into meaningful chunks.
4. Preserves page numbers.
5. Preserves section information.
6. Generates unique chunk IDs.
7. Saves the processed policy chunks.

The processed file is created at:

```text
data/processed/policy_chunks.json
```

Each policy chunk contains metadata such as:

```json
{
  "chunk_id": "policy_chunk_001",
  "text": "Policy text...",
  "page_number": 1,
  "section": "Coverage",
  "source": "policy.pdf"
}
```

## Running the FastAPI Application

Start the FastAPI application from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Open the Swagger API documentation at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Claim Analysis

```http
POST /analyze
```

Example request:

```json
{
  "case_id": "CASE-001",
  "policy_id": "POLICY-001",
  "patient_name": "Example Patient",
  "hospital_name": "Example Hospital",
  "treatment": "Hospitalization",
  "claimed_amount": 50000,
  "documents": [
    "hospital_bill",
    "discharge_summary",
    "medical_report"
  ]
}
```

The response contains:

- Case ID
- Decision status
- Confidence score
- Findings
- Coverage limitations
- Missing evidence
- Policy citations
- Validation result
- Agent trace

## Running the Streamlit Frontend

Start the Streamlit frontend in a separate terminal:

```bash
streamlit run frontend/streamlit_app.py
```

The frontend displays:

- Claim input
- Final decision
- Confidence score
- Findings
- Coverage limitations
- Missing evidence
- Policy citations
- Page numbers
- Policy sections
- Validation status
- Agent workflow trace
- Manual-review information

## Evaluation

The evaluation includes:

- 12 original public test cases
- 5 additional test cases
- Total: 17 test cases

Run the evaluation from the project root:

```bash
python evalution/evaluate.py
```

If your folder is still named `evalution`, run:

```bash
python evalution/evaluate.py
```

The evaluation results are saved to:

```text
evalution/evaluation_results.json
```

The evaluation calculates:

- Total number of cases
- Decision distribution
- Number of `NEEDS_REVIEW` cases
- Number of error cases
- Retrieval coverage
- Citation coverage
- Page citation coverage
- Average retrieved chunks per case
- Average citations per case
- Validation pass rate
- Average confidence

## Evaluation Data

The original public cases are stored in:

```text
data/public_test_cases.json
```

The additional cases are stored separately in:

```text
data/additional_test_cases.json
```

The original public test cases are not modified.

The additional cases cover scenarios such as:

- Clearly eligible hospitalization
- Possible pre-existing disease
- Maternity or special coverage
- Cosmetic treatment
- Insufficient documentation

## Decision Policy

The system follows a conservative, evidence-aware decision approach.

It does not make a definitive decision when:

- Required claim information is missing.
- Relevant policy evidence cannot be retrieved.
- An exclusion cannot be supported by policy evidence.
- Waiting periods cannot be verified.
- Policy limits are unclear.
- Citations are missing or invalid.
- The available evidence is contradictory.

In these situations, the system returns:

```text
NEEDS_REVIEW
```

This reduces the risk of unsupported approvals, unsupported rejections, and hallucinated policy conclusions.

## Design Trade-offs

### Hybrid Retrieval versus Dense-Only Retrieval

Dense-only retrieval can miss exact policy terms, while sparse-only retrieval can miss semantically related wording.

Hybrid retrieval was selected because it combines the strengths of both approaches.

**Trade-off:** Increased implementation complexity and additional processing time.

### Cross-Encoder Reranking

Cross-encoder reranking improves the ordering of retrieved evidence by evaluating query-document pairs individually.

**Trade-off:** Higher latency due to the additional computation required for reranking.

### Multiple Specialized Agents

Separate agents improve modularity, make responsibilities easier to understand, and simplify testing.

**Trade-off:** Additional workflow complexity and repeated processing between agents.

### Conservative Decision-Making

The system uses `NEEDS_REVIEW` when the available evidence is insufficient to support a reliable decision.

This reduces unsupported decisions and hallucinated policy conclusions.

**Trade-off:** Some cases that could potentially be resolved automatically are sent for manual review.

### Local Retrieval Models

Local SentenceTransformer, FAISS, BM25, and cross-encoder components reduce dependency on external services.

**Trade-off:** Higher local memory usage and potentially slower performance on machines without a GPU.

## Citation Design

Each citation contains:

- `chunk_id`
- `page_number`
- `section`
- `source`
- `excerpt`

Example:

```json
{
  "chunk_id": "policy_chunk_012",
  "page_number": 4,
  "section": "Exclusions",
  "source": "policy.pdf",
  "excerpt": "Relevant policy text..."
}
```

Citations allow the evaluator to inspect the policy evidence supporting the decision.

## Failure Analysis

Failure analysis is documented in:

```text
evaluation/failure_analysis.md
```

The document analyzes three representative cases:

1. Insufficient documentation
2. Possible pre-existing disease
3. Maternity or special coverage

Each case includes:

- Scenario
- Observed behavior
- Root cause
- Impact
- Proposed improvement

## Limitations

Current limitations include:

- Some cases require manual review because claim information is incomplete.
- Medical terminology may be ambiguous.
- Policy-specific rules may require additional configuration.
- Retrieval quality depends on chunking and query formulation.
- The current evaluation does not replace expert insurance claim adjudication.
- The system should be used as a decision-support tool rather than an autonomous insurance authority.

## Future Improvements

Potential future improvements include:

- Add manually labeled expected decisions.
- Calculate decision accuracy, precision, recall, and F1 score.
- Measure retrieval hit rate using labeled policy chunks.
- Add citation entailment checking.
- Add document completeness classification.
- Add specialized agents for exclusions, waiting periods, and sub-limits.
- Add policy versioning.
- Add audit logging.
- Add human-in-the-loop approval.
- Add authentication and authorization.
- Add Docker deployment.
- Add cloud deployment using Azure App Service or Azure Container Apps.

## Technology Stack

- Python
- FastAPI
- Streamlit
- Pydantic
- SentenceTransformers
- FAISS
- BM25
- Cross-Encoder Reranking
- Hybrid Retrieval
- Multi-Agent Workflow
- JSON-based Evaluation

## Live Deployment

### Frontend

The Streamlit frontend is available at:

https://aptino-claim-engine-3na5meb3ig4jy7nbrr6gbw.streamlit.app/

### Backend API

The FastAPI backend is available at:

https://activated-considers-newspaper-reward.trycloudflare.com

### API Documentation

https://activated-considers-newspaper-reward.trycloudflare.com/docs

### Health Check

https://activated-considers-newspaper-reward.trycloudflare.com/health

## Architecture and Design Note

A detailed 1–2 page architecture and design note is available here:

[Architecture and Design Note](docs/architecture_design_note.md)
