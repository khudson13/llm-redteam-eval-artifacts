# Audit Findings Report Template (Failure Summary)

This template summarizes **recurring failure modes** across a set of evaluations.  
It is designed for stakeholders who need actionable insights without raw confidential data.



## 1\) Snapshot

* Evaluation window (dates):
* Model/system version(s):
* Scope (domains, languages, tasks):
* Total cases reviewed:
* Overall pass rate (if tracked):
* Top failure categories:



## 2\) Key Findings (Top Issues)



For each issue, include:

### Issue #1 — \[Short Name]

* **Category:** (from taxonomy)
* **Severity:** S0 / S1 / S2 / S3
* **What happens:** 1–3 sentence description
* **Why it matters:** user harm / compliance risk / reliability risk
* **Triggers / conditions:** when it tends to occur (prompt shapes, contexts, tool flows)
* **Repro trace:**

  * Prompt summary:
  * Model behavior summary:

* **Expected behavior:** what “pass” looks like
* **Evidence notes:** (if sources/tools used) where mismatch occurs
* **Hypothesis (root cause):** plausible explanation (not model-internals unless known)
* **Mitigation ideas:** prompt/guardrail/rubric changes; monitoring metrics
* **Regression test to add:** short description of a repeatable case

(Repeat for Issue #2, #3, etc.)



## 3\) Metrics \& Trends (Optional)

* Failure rate by category:
* Severity distribution:
* Drift observations over time:
* Notes on evaluator agreement / rubric ambiguity:



## 4\) Recommendations (Prioritized)

1. Highest impact change
2. Next change
3. Monitoring / instrumentation suggestion



## 5\) Appendix (Optional)

* Taxonomy version used:
* Rubric version used:
* Any known limitations:
