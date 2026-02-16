# Manual Red Team Playbook (High-Level Patterns)

This playbook lists **high-level, non-actionable** patterns for manual adversarial probing.  
It is designed for **testing robustness**, not enabling misuse.



## Principles

* Prefer **reproducible prompts** and document exact conversation traces.
* Change **one variable at a time** (wording, role framing, constraints, context).
* Track: expected behavior, observed behavior, failure tags, and severity.



## Patterns (Non-Exhaustive)



### 1\) Rephrasing Robustness

**Goal:** Check if safety/compliance and correctness hold under paraphrase.  
**Method:** Ask the same request in multiple neutral formulations and compare outcomes.



### 2\) Multi-Turn Pressure / Refusal Erosion

**Goal:** Check if the model maintains boundaries across turns.  
**Method:** Begin with benign context; over several turns, introduce pressure, urgency, or reframing.  
**Expected:** Consistent refusal/safe alternative when needed; no “gradual give-in.”



### 3\) Instruction Hierarchy Conflicts

**Goal:** Test whether higher-priority constraints remain dominant.  
**Method:** Introduce conflicting instructions over time; see if the model incorrectly privileges user-supplied constraints.



### 4\) Role / Persona Framing

**Goal:** Test whether roleplay changes compliance or factuality.  
**Method:** Present the model as a “role” (e.g., assistant, reviewer, teacher) and see whether behavior shifts incorrectly.



### 5\) Context Poisoning / False Premises

**Goal:** Test whether the model accepts injected false context as truth.  
**Method:** Provide questionable “facts” earlier; later ask for conclusions based on them.  
**Expected:** Challenge dubious premises or clearly label uncertainty.



### 6\) Grounding Stress (When Sources Are Provided)

**Goal:** Check faithfulness to provided evidence.  
**Method:** Provide sources with subtle contradictions or partial coverage; ask for an answer with citations.  
**Expected:** Accurate citation mapping, uncertainty when evidence conflicts, no unsupported claims.



### 7\) Tool Trace Consistency (When Tools Are Used)

**Goal:** Verify correct tool selection and incorporation of tool results.  
**Method:** Use scenarios that require a tool; verify final answer matches tool output and avoids invented steps.



### 8\) Edge-Case Compliance / Over-Refusal

**Goal:** Ensure the model doesn’t refuse safe requests unnecessarily.  
**Method:** Use borderline-but-allowed scenarios; evaluate whether it responds safely and helpfully.



## Output Template (minimum)

For each test case, record:

* Scenario name
* Expected behavior
* Conversation trace (prompt(s) + model response(s))
* Pass/Fail + rationale
* Failure tags (taxonomy)
* Severity
* Notes (hypothesis about trigger/cause)
