# Failure Analysis

## Purpose

This document analyzes three representative failure cases from the **Policy-Aware Multi-Agent RAG Claim Decision Engine** evaluation.

The purpose is to identify limitations in retrieval, evidence verification, decision-making, and validation, and to propose improvements for future iterations.

---

## Failure Case 1: Insufficient Documentation

### Case ID

`ADDITIONAL-005`

### Scenario

The claim contains incomplete or insufficient supporting documentation.

### Observed Behavior

The system returns:

```text
NEEDS_REVIEW
```

### Root Cause

The workflow cannot confidently verify all required claim facts from the available input.

Important information may be missing, such as:

* Hospital or treatment records.
* Diagnosis details.
* Bills or expense documents.
* Admission and discharge information.
* Required claim forms.
* Supporting medical reports.

The decision agent avoids making a definitive approval or rejection when important evidence is unavailable.

### Impact

The claim cannot be automatically approved or rejected and must be reviewed by a human evaluator.

### Proposed Improvements

* Add document completeness checks before policy retrieval.
* Identify required documents based on claim type.
* Return a structured list of missing documents.
* Add confidence thresholds for automatic decisions.
* Route incomplete claims to a human reviewer.
* Add a dedicated documentation verification agent.

---

## Failure Case 2: Possible Pre-existing Disease

### Case ID

`ADDITIONAL-002`

### Scenario

The claim may involve a medical condition that existed before the policy coverage period.

### Observed Behavior

The system returns:

```text
NEEDS_REVIEW
```

### Root Cause

The available claim data does not conclusively establish:

* When the medical condition first occurred.
* Whether the condition existed before policy inception.
* Whether the policy contains an applicable pre-existing disease exclusion.
* Whether the applicable waiting period has been completed.
* Whether the submitted medical records support the exclusion.

The system therefore does not apply an exclusion without sufficient evidence.

### Impact

The claim requires manual review because the available information is insufficient to determine whether the condition is covered.

### Proposed Improvements

* Extract and compare relevant medical dates.
* Retrieve the exact pre-existing disease clause.
* Retrieve applicable waiting-period clauses.
* Add a dedicated pre-existing-condition verification agent.
* Require explicit policy and claim evidence before applying an exclusion.
* Include the relevant policy citation in the final explanation.

---

## Failure Case 3: Maternity or Special Coverage

### Case ID

`ADDITIONAL-003`

### Scenario

The claim involves maternity-related treatment or another special coverage category.

### Observed Behavior

The system returns:

```text
NEEDS_REVIEW
```

### Root Cause

Special coverage categories may depend on several policy conditions, including:

* Whether maternity coverage is included.
* Whether the applicable waiting period has been completed.
* Whether a coverage limit or sub-limit applies.
* Whether the treatment is included within the policy scope.
* Whether the required documents have been submitted.
* Whether any policy-specific exclusions apply.

The system does not have enough verified evidence to determine all of these conditions automatically.

### Impact

The claim is routed for manual review instead of receiving a definitive decision.

### Proposed Improvements

* Add special-coverage classification.
* Retrieve maternity-specific policy sections.
* Extract waiting periods and sub-limits.
* Compare the claim amount with applicable limits.
* Add rule-based checks for required maternity documents.
* Add a dedicated special-coverage agent.
* Require citations for all coverage and limitation claims.

---

## Common Root Causes

The three cases show several common limitations:

1. Incomplete claim information.
2. Missing supporting documents.
3. Ambiguous medical or treatment descriptions.
4. Insufficient evidence for applying exclusions.
5. Missing or unclear waiting-period information.
6. Lack of specialized rules for certain coverage categories.
7. Conservative validation that routes unsupported decisions to `NEEDS_REVIEW`.

---

## Recommended Improvements

### 1. Retrieval Improvements

* Increase retrieval diversity by combining dense and sparse retrieval.
* Use section-aware document chunking.
* Add metadata filters for policy sections.
* Tune dense and sparse retrieval weights.
* Add query expansion for medical and insurance terminology.
* Evaluate retrieval using manually labeled relevant policy chunks.

### 2. Decision-Making Improvements

* Separate factual extraction from policy interpretation.
* Require evidence before applying an exclusion.
* Add explicit handling for waiting periods and coverage limits.
* Use structured rule evaluation before final decision generation.
* Prevent the system from inferring missing medical or policy facts.
* Route ambiguous cases to human review.

### 3. Validation Improvements

* Verify every citation's chunk ID.
* Verify page numbers against the source policy.
* Check that cited excerpts actually support the decision.
* Check that every material finding has supporting evidence.
* Downgrade unsupported decisions to `NEEDS_REVIEW`.

### 4. Evaluation Improvements

* Add manually labeled expected decisions.
* Measure decision accuracy, precision, recall, and F1 score.
* Measure retrieval hit rate.
* Measure citation correctness.
* Track false approvals and false rejections separately.
* Add regression tests for previously failing cases.
* Re-run evaluation after every retrieval or decision-rule change.

---

## Conclusion

These failure cases demonstrate the importance of evidence-grounded decision-making in policy-aware claim processing.

The system currently takes a conservative approach when required information is missing or policy conditions cannot be verified. This helps prevent unsupported approval or rejection decisions, but increases the number of claims requiring manual review.

Future improvements should focus on:

* More reliable document retrieval.
* Specialized verification agents.
* Explicit policy-rule evaluation.
* Stronger citation and evidence validation.
* Comprehensive regression testing.

The objective is to improve automation while maintaining traceability, evidence grounding, and safe handling of uncertain claims.
