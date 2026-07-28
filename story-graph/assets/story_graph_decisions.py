#!/usr/bin/env python3
"""Score the skill's inclusion & resolution decisions against a fixture corpus.

`reference/decisions.md` states the rules. This measures whether they are actually
followed, because a decision layer you cannot score is one you can only argue about:
without a number, every prompt edit is a guess and no edit can be shown to be an
improvement.

Two halves, and the first needs no model at all:

  * **structural** (always, in CI) — is the corpus itself well-formed? A case with an
    unparseable expectation silently scores as a pass, so the corpus is checked before
    it is trusted.
  * **scored** (opt-in) — put each case to a model, compare against the recorded
    correct call, print correct/total per category.

Every category carries BOTH polarities on purpose. Without controls a degenerate
strategy — always "ambiguous", always "unsupported", always propose a row — scores
well while deciding nothing. The controls are what make the number mean something.

`story_graph.py` never imports this; nothing here runs during validate or compile.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# ask -> (what the model is asked for, the JSON shape it must answer in)
ASKS = {
    "entities": ("How many DISTINCT people appear, and which surface forms refer to which?",
                 '{"people": [{"canonical": "<id>", "surfaces": ["..."]}], "ambiguous": true|false}'),
    "inclusion": ("Which numbered sentences earn a Proposition row? A sentence earns one only if "
                  "a later chapter could contradict it. Atmosphere and scenery do not.",
                  '{"rows": [<sentence numbers>]}'),
    "temporal": ("Are these two records a genuine contradiction, or one state changing over time?",
                 '{"verdict": "contradiction" | "state-change"}'),
    "basis": ("Does the scene actually support the claim, or is the claim an inference with no "
              "line to point at?",
              '{"supported": true|false}'),
}

SYSTEM = ("You maintain a story graph: a structured model of a manuscript's hidden state. "
          "Answer ONLY with the requested JSON object and nothing else. "
          "Do not invent facts the text does not support.")


def _parse(text, name):
    head, sections, cur = {}, {}, None
    for line in text.splitlines():
        if line.startswith("# "):
            head["id"] = line[2:].strip()
        elif line.startswith("## "):
            cur = line[3:].strip().lower()
            sections[cur] = []
        elif cur is None and line.startswith("- ") and ":" in line:
            k, v = line[2:].split(":", 1)
            head[k.strip()] = v.strip()
        elif cur is not None:
            sections[cur].append(line)
    expect = {}
    for line in sections.get("expect", []):
        if line.startswith("- ") and ":" in line:
            k, v = line[2:].split(":", 1)
            expect[k.strip()] = v.strip()
    return {"file": name, "id": head.get("id", name), "category": head.get("category", ""),
            "ask": head.get("ask", ""), "expect": expect,
            "scene": "\n".join(sections.get("scene", [])).strip(),
            "claim": "\n".join(sections.get("claim", [])).strip(),
            "trap": "\n".join(sections.get("trap", [])).strip()}


def load_cases(dirpath):
    return [_parse(p.read_text(encoding="utf-8"), p.name)
            for p in sorted(Path(dirpath).glob("*.md"))]


def check_corpus(cases):
    """Structural problems with the corpus itself. An unparseable expectation would
    silently grade as correct, so this runs before anything is scored."""
    problems = []
    if not cases:
        problems.append("no cases found")
    seen = set()
    for c in cases:
        w = f"[{c['file']}]"
        if c["id"] in seen:
            problems.append(f"{w} duplicate case id '{c['id']}'")
        seen.add(c["id"])
        if c["ask"] not in ASKS:
            problems.append(f"{w} unknown ask '{c['ask']}' (expected one of {sorted(ASKS)})")
        if not c["scene"]:
            problems.append(f"{w} empty Scene")
        if not c["trap"]:
            problems.append(f"{w} no Trap recorded — the case doesn't say what it is testing")
        if not c["expect"]:
            problems.append(f"{w} no Expect block — this case can never fail")
        for k in c["expect"]:
            if k not in ("entity_count", "ambiguity", "rows", "verdict", "supported"):
                problems.append(f"{w} unknown expectation key '{k}'")
        if c["ask"] == "basis" and not c["claim"]:
            problems.append(f"{w} a 'basis' case needs a Claim section")
    # Controls: a category with only one answer can be passed by always saying it.
    for cat in {c["category"] for c in cases}:
        vals = [tuple(sorted(c["expect"].items())) for c in cases if c["category"] == cat]
        if len(vals) > 1 and len(set(vals)) == 1:
            problems.append(f"category '{cat}' has no control — every case expects the same "
                            f"answer, so a fixed reply scores 100%")
    return problems


def prompt_for(case):
    question, shape = ASKS[case["ask"]]
    body = [question, "", "SCENE:", case["scene"]]
    if case["claim"]:
        body += ["", "CLAIM:", case["claim"]]
    body += ["", f"Answer with exactly this JSON shape: {shape}"]
    return SYSTEM, "\n".join(body)


def _json_from(text):
    """Models wrap JSON in fences, prose, or a reasoning preamble, and sometimes emit
    more than one object. Take the first BALANCED object rather than the first `{` to
    the last `}` — that greedy span silently swallows a second object and fails."""
    s = text or ""
    start = s.find("{")
    while start != -1:
        depth, instr, esc = 0, False, False
        for i in range(start, len(s)):
            ch = s[i]
            if instr:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    instr = False
                continue
            if ch == '"':
                instr = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(s[start:i + 1])
                    except Exception:
                        break
        start = s.find("{", start + 1)
    return None


def _norm_rows(v):
    return {int(x) for x in re.findall(r"\d+", str(v or ""))}


def grade(case, answer):
    """(points, total, notes). Each recorded expectation is worth one point."""
    exp, notes, pts = case["expect"], [], 0
    if answer is None:
        return 0, len(exp), ["no parseable JSON in the reply"]
    for k, want in exp.items():
        ok = False
        if k == "entity_count":
            got = len(answer.get("people") or [])
            ok = str(got) == want.strip()
            notes.append(f"entity_count want {want} got {got}")
        elif k == "ambiguity":
            got = bool(answer.get("ambiguous"))
            ok = got == (want.strip().lower() in ("yes", "true"))
            notes.append(f"ambiguity want {want} got {'yes' if got else 'no'}")
        elif k == "rows":
            got, wnt = _norm_rows(answer.get("rows")), _norm_rows(want)
            ok = got == wnt
            notes.append(f"rows want {sorted(wnt) or '[]'} got {sorted(got) or '[]'}")
        elif k == "verdict":
            got = str(answer.get("verdict", "")).strip().lower()
            ok = got == want.strip().lower()
            notes.append(f"verdict want {want} got {got or '-'}")
        elif k == "supported":
            got = bool(answer.get("supported"))
            ok = got == (want.strip().lower() in ("yes", "true"))
            notes.append(f"supported want {want} got {'yes' if got else 'no'}")
        pts += 1 if ok else 0
        notes[-1] += "  " + ("ok" if ok else "MISS")
    return pts, len(exp), notes


def run(dirpath, chat=None, verbose=True):
    """Report text + (points, total). With chat=None only the structural half runs."""
    cases = load_cases(dirpath)
    problems = check_corpus(cases)
    out = [f"DECISION CORPUS — {len(cases)} case(s) in {dirpath}", "=" * 56]
    by_cat = {}
    for c in cases:
        by_cat.setdefault(c["category"], []).append(c["id"])
    for cat, ids in sorted(by_cat.items()):
        out.append(f"  {cat:<12} {len(ids):>2}  {', '.join(ids)}")
    out.append("")
    if problems:
        out.append(f"STRUCTURE — {len(problems)} problem(s):")
        out += [f"  ! {p}" for p in problems]
        return "\n".join(out), (0, 0)
    out.append("STRUCTURE — ok (every case has a scene, a trap, a checkable expectation, "
               "and every category has a control)")
    if chat is None:
        out += ["", "No provider configured, so the scored half did not run.",
                "  story_graph.py decisions <dir> --provider ollama --model <id>"]
        return "\n".join(out), (0, 0)

    out += ["", "SCORED"]
    tot_p = tot_t = 0
    per_cat, fmt, retried = {}, [], []
    for c in cases:
        system, user = prompt_for(c)
        try:
            answer = _json_from(chat(system, user))
            if answer is None:
                # Failing to emit JSON is a DIFFERENT failure from deciding wrongly, and
                # it flakes run to run. Retry once (the pattern the Ask tab already uses)
                # so the score reflects judgement, not formatting luck.
                answer = _json_from(chat(system, user + "\n\nReply with the JSON object ONLY. "
                                                       "No prose, no explanation, no code fence."))
                if answer is not None:
                    retried.append(c["id"])
        except Exception as e:                       # a dead provider must not look like a wrong answer
            out.append(f"  [ERR ] {c['id']:<32} {e}")
            continue
        p, t, notes = grade(c, answer)
        tot_p += p
        tot_t += t
        a, b = per_cat.get(c["category"], (0, 0))
        per_cat[c["category"]] = (a + p, b + t)
        if answer is None:
            fmt.append(c["id"])
            mark = "FMT "
        else:
            mark = "ok  " if p == t else "MISS"
        out.append(f"  [{mark}] {c['id']:<32} {p}/{t}")
        if verbose and p != t:
            out += [f"          {n}" for n in notes]
            out.append(f"          trap: {c['trap'].splitlines()[0] if c['trap'] else ''}")
    out.append("")
    for cat, (p, t) in sorted(per_cat.items()):
        out.append(f"  {cat:<12} {p}/{t}")
    out.append(f"  {'TOTAL':<12} {tot_p}/{tot_t}")
    if retried:
        out.append(f"  (recovered by one retry: {', '.join(retried)})")
    if fmt:
        out.append(f"  ! {len(fmt)} case(s) never returned JSON ({', '.join(fmt)}) — scored 0, but "
                   f"that is a compliance failure, not a wrong decision. Judge the model on the "
                   f"other {tot_t - sum(len(c['expect']) for c in cases if c['id'] in fmt)} point(s).")
    return "\n".join(out), (tot_p, tot_t)
