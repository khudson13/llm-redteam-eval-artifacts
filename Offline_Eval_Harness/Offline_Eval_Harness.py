#!/usr/bin/env python3
"""
Offline LLM Eval Harness v0.1 (stdlib-only)

Workflow:
- Load cases from cases/cases.jsonl (JSONL: one object per line)
- For each case:
  - Display sources + turns
  - Paste model response (end with <<<END>>>)
  - Enter evaluation (PASS/FAIL, tags, severity_observed, notes)
- Write:
  - runs/<run_id>/raw_outputs.jsonl
  - runs/<run_id>/judgments.jsonl
  - runs/<run_id>/summary.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

ALLOWED_SEVERITIES = {"S0", "S1", "S2", "S3"}
END_SENTINEL = "<<<END>>>"


def eprint(*args: Any) -> None:
    print(*args, file=sys.stderr)


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    raise ValueError("JSONL line must be an object")
                cases.append(obj)
            except Exception as ex:
                raise ValueError(f"Failed parsing JSONL at {path}:{i}: {ex}") from ex
    return cases


def validate_case(case: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Minimal strict validation. Returns (ok, errors)."""
    errors: List[str] = []

    def req_str(field: str) -> None:
        if field not in case or not isinstance(case[field], str) or not case[field].strip():
            errors.append(f"Missing/invalid required string field: {field}")

    def req_list_str(field: str) -> None:
        if field not in case or not isinstance(case[field], list) or not all(isinstance(x, str) for x in case[field]):
            errors.append(f"Missing/invalid required array<string> field: {field}")

    req_str("id")
    req_str("title")
    req_str("category")
    req_list_str("tags")
    req_str("severity_expectation")

    sev = case.get("severity_expectation")
    if isinstance(sev, str) and sev not in ALLOWED_SEVERITIES:
        errors.append(f"severity_expectation must be one of {sorted(ALLOWED_SEVERITIES)}")

    turns = case.get("turns")
    if not isinstance(turns, list) or not turns:
        errors.append("Missing/invalid required field: turns (non-empty array)")
    else:
        for t in turns:
            if not isinstance(t, dict):
                errors.append("turns elements must be objects")
                break
            role = t.get("role")
            content = t.get("content")
            if role not in {"system", "user", "assistant"}:
                errors.append("turns[].role must be system|user|assistant")
                break
            if not isinstance(content, str):
                errors.append("turns[].content must be string")
                break

    eb = case.get("expected_behavior")
    if not isinstance(eb, dict):
        errors.append("Missing/invalid required field: expected_behavior (object)")
    else:
        for sub in ("must_do", "must_not_do", "pass_criteria"):
            v = eb.get(sub)
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                errors.append(f"expected_behavior.{sub} must be array<string>")

    # Optional sources validation
    if "sources" in case:
        sources = case["sources"]
        if not isinstance(sources, list):
            errors.append("sources must be an array if present")
        else:
            for s in sources:
                if not isinstance(s, dict):
                    errors.append("sources[] elements must be objects")
                    break
                for sub in ("source_id", "title", "text"):
                    if sub not in s or not isinstance(s[sub], str):
                        errors.append(f"sources[] missing/invalid field: {sub}")
                        break

    return (len(errors) == 0), errors


def prompt_multiline(label: str) -> str:
    print()
    print(f"{label}")
    print(f"Paste the model response. End with a line containing exactly: {END_SENTINEL}")
    lines: List[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == END_SENTINEL:
            break
        lines.append(line)
    return "\n".join(lines).strip()


def prompt_choice(prompt: str, choices: List[str]) -> str:
    choices_lower = {c.lower(): c for c in choices}
    while True:
        val = input(prompt).strip()
        if not val:
            continue
        key = val.lower()
        if key in choices_lower:
            return choices_lower[key]
        print(f"Please enter one of: {', '.join(choices)}")


def prompt_severity(prompt: str) -> str:
    while True:
        val = input(prompt).strip().upper()
        if val in ALLOWED_SEVERITIES:
            return val
        print(f"Please enter severity one of: {', '.join(sorted(ALLOWED_SEVERITIES))}")


def prompt_tags(prompt: str) -> List[str]:
    val = input(prompt).strip()
    if not val:
        return []
    # comma-separated
    tags = [t.strip() for t in val.split(",")]
    return [t for t in tags if t]


def safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def render_case(case: Dict[str, Any]) -> None:
    print("\n" + "=" * 80)
    print(f"CASE {case['id']}: {case['title']}")
    print(f"Category: {case['category']} | Expected Severity on Fail: {case['severity_expectation']}")
    print(f"Tags: {', '.join(case.get('tags', []))}")
    print("-" * 80)

    sources = case.get("sources") or []
    if sources:
        print("\nSOURCES PROVIDED:")
        for s in sources:
            print(f"  [{s['source_id']}] {s['title']}")
            # keep display tidy
            text = s["text"].strip()
            print(f"    {text}")

    print("\nTURNS:")
    for t in case["turns"]:
        role = t["role"].upper()
        content = t["content"].strip()
        print(f"\n[{role}]\n{content}")

    eb = case["expected_behavior"]
    print("\nEXPECTED BEHAVIOR (for evaluator):")
    print("  MUST DO:")
    for x in eb["must_do"]:
        print(f"   - {x}")
    print("  MUST NOT DO:")
    for x in eb["must_not_do"]:
        print(f"   - {x}")
    print("  PASS CRITERIA:")
    for x in eb["pass_criteria"]:
        print(f"   - {x}")


def write_jsonl(path: str, rows: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_summary_md(path: str, run_id: str, outputs: List[Dict[str, Any]], judgments: List[Dict[str, Any]]) -> None:
    # Join on case_id
    j_by_case = {j["case_id"]: j for j in judgments}
    pass_count = 0
    fail_count = 0
    by_category = Counter()
    by_category_pass = Counter()
    by_tag = Counter()
    by_fail_tag = Counter()
    severities = Counter()

    for out in outputs:
        cid = out["case_id"]
        cat = out.get("category", "Unknown")
        by_category[cat] += 1
        j = j_by_case.get(cid)
        if not j:
            continue
        if j["outcome"] == "PASS":
            pass_count += 1
            by_category_pass[cat] += 1
        else:
            fail_count += 1
            for t in j.get("tags", []):
                by_fail_tag[t] += 1
        for t in j.get("tags", []):
            by_tag[t] += 1
        sev = j.get("severity_observed")
        if sev:
            severities[sev] += 1

    total = pass_count + fail_count
    pass_rate = (pass_count / total) if total else 0.0

    lines: List[str] = []
    lines.append(f"# Run Summary — {run_id}")
    lines.append("")
    lines.append(f"- Total cases scored: **{total}**")
    lines.append(f"- PASS: **{pass_count}**")
    lines.append(f"- FAIL: **{fail_count}**")
    lines.append(f"- Pass rate: **{pass_rate:.1%}**")
    lines.append("")

    lines.append("## By Category")
    lines.append("")
    lines.append("| Category | Cases | Pass | Pass Rate |")
    lines.append("|---|---:|---:|---:|")
    for cat, n in by_category.most_common():
        p = by_category_pass.get(cat, 0)
        pr = (p / n) if n else 0.0
        lines.append(f"| {cat} | {n} | {p} | {pr:.1%} |")
    lines.append("")

    if severities:
        lines.append("## Severity Observed (from judgments)")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|---|---:|")
        for sev in ["S0", "S1", "S2", "S3"]:
            if sev in severities:
                lines.append(f"| {sev} | {severities[sev]} |")
        lines.append("")

    if by_fail_tag:
        lines.append("## Top Failure Tags (FAIL cases)")
        lines.append("")
        lines.append("| Tag | Count |")
        lines.append("|---|---:|")
        for tag, n in by_fail_tag.most_common(15):
            lines.append(f"| {tag} | {n} |")
        lines.append("")

    if by_tag:
        lines.append("## Tags (All judgments)")
        lines.append("")
        lines.append("| Tag | Count |")
        lines.append("|---|---:|")
        for tag, n in by_tag.most_common(20):
            lines.append(f"| {tag} | {n} |")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="cases/cases.jsonl", help="Path to cases.jsonl")
    ap.add_argument("--run-id", default="", help="Optional run id; default is timestamp")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of cases (0 = all)")
    ap.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    args = ap.parse_args()

    run_id = args.run_id.strip() or dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    cases_path = args.cases

    cases = load_jsonl(cases_path)

    # validate all cases up-front
    bad = 0
    for c in cases:
        ok, errs = validate_case(c)
        if not ok:
            bad += 1
            eprint(f"\nINVALID CASE {c.get('id','<no id>')}:")
            for err in errs:
                eprint(f"  - {err}")
    if bad:
        eprint(f"\nFound {bad} invalid case(s). Fix schema errors before running.")
        return 2

    start = max(0, args.start)
    subset = cases[start:]
    if args.limit and args.limit > 0:
        subset = subset[: args.limit]

    run_dir = os.path.join("runs", run_id)
    safe_mkdir(run_dir)

    outputs: List[Dict[str, Any]] = []
    judgments: List[Dict[str, Any]] = []

    print(f"\nStarting run: {run_id}")
    print(f"Cases: {len(subset)} (from {cases_path}, start={start}, limit={args.limit or 'all'})")

    for idx, case in enumerate(subset, start=1):
        render_case(case)

        model_response = prompt_multiline("MODEL RESPONSE")
        if not model_response:
            print("No response entered. You can still score, but output will be empty.")

        outcome = prompt_choice("Outcome (PASS/FAIL): ", ["PASS", "FAIL"])
        tags = prompt_tags("Tags (comma-separated; blank ok): ")
        severity_observed = prompt_severity("Severity observed (S0/S1/S2/S3): ")
        notes = input("Notes (optional; blank ok): ").strip()

        outputs.append(
            {
                "run_id": run_id,
                "case_id": case["id"],
                "title": case["title"],
                "category": case["category"],
                "case_tags": case.get("tags", []),
                "timestamp_utc": dt.datetime.utcnow().isoformat() + "Z",
                "model_response": model_response,
            }
        )

        judgments.append(
            {
                "run_id": run_id,
                "case_id": case["id"],
                "outcome": outcome,
                "tags": tags,
                "severity_observed": severity_observed,
                "notes": notes,
            }
        )

        print("\nSaved. Moving to next case.")
        print("=" * 80)

    raw_path = os.path.join(run_dir, "raw_outputs.jsonl")
    j_path = os.path.join(run_dir, "judgments.jsonl")
    summary_path = os.path.join(run_dir, "summary.md")

    write_jsonl(raw_path, outputs)
    write_jsonl(j_path, judgments)
    write_summary_md(summary_path, run_id, outputs, judgments)

    print("\nRun complete.")
    print(f"- Raw outputs:   {raw_path}")
    print(f"- Judgments:     {j_path}")
    print(f"- Summary:       {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
