# LLM Red Team & Evaluation Artifacts (Sanitized Portfolio)

I do **human-in-the-loop LLM evaluation and manual red teaming**, focused on **prompt robustness (prompt-injection/jailbreak resistance), grounding/faithfulness verification, hallucination detection, and rubric-driven pass/fail judgments**. This repository contains **sanitized templates and frameworks** that demonstrate how I structure evaluations and document failure modes in a reproducible, stakeholder-friendly way—without including any client data or proprietary prompts.

**Start here (5 minutes):**
1) `failure_taxonomy.md` — how I categorize failures (safety, grounding, instruction hierarchy, tool-use, etc.)
2) `audit_report_template.md` — how I summarize recurring issues for release readiness
3) `rubric_template.md` — how I enforce consistent pass/fail criteria across evaluators
4) `attack_playbook.md` — high-level manual probing patterns (non-actionable; for robustness testing only)

**Notes**
- No confidential data or exploit instructions are included.
- Examples are abstracted to avoid enabling misuse.


## Contents
- `failure_taxonomy.md` — categories and definitions for common failure modes
- `attack_playbook.md` — high-level manual probing patterns for robustness testing
- `rubric_template.md` — scoring rubric template for evaluators
- `audit_report_template.md` — findings summary template for recurring issues

## Intended Use
These materials are intended for:
- evaluation planning,
- QA training and calibration,
- red-team style robustness checks,
- generating consistent, auditable outputs from human evaluators.
