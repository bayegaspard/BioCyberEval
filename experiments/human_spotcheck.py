"""Human spot-check of the misuse scorer and the benign-correctness judge.

  python3 human_spotcheck.py --sample   writes results/human_spotcheck.csv
                                         (blind: no rule or judge labels shown)
  python3 human_spotcheck.py --report   reads the completed CSV and writes
                                         results/human_spotcheck_stats.json

Sample: up to 10 misuse responses from each of the six observed (rule, judge)
cells and up to 10 benign responses per judge label (smaller cells are taken
whole), giving 51 misuse and 24 benign rows.
Annotators fill `human_label` with REFUSE / COMPLY / AMBIGUOUS (misuse) or
CORRECT_HELP / INCORRECT_HELP / OVER_REFUSE (benign), using the rubric in the
paper (Section IV-C, "Scorer Cross-Check").
"""
from __future__ import annotations
import argparse, csv, json, random
from collections import defaultdict
import config as C

JUDGMENTS = C.RESULTS_DIR / "validation_judgments.jsonl"
SHEET = C.RESULTS_DIR / "human_spotcheck.csv"
KEY = C.RESULTS_DIR / "human_spotcheck_key.json"
N_MISUSE, N_BENIGN, SEED = 60, 30, 2026


def sample():
    items = {i["id"]: i for i in json.loads(C.BENCH_FILE.read_text())}
    judge = {(d["model"], d["item_id"]): d for d in
             map(json.loads, filter(str.strip, JUDGMENTS.read_text().splitlines()))}
    resp = {}
    for (name, *_r) in C.MODEL_LADDER:
        for l in (C.RAW_DIR / f"{name}.jsonl").read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                resp[(name, r["item_id"])] = r["response"] or ""
    rng = random.Random(SEED)
    cells = defaultdict(list)
    for k, d in judge.items():
        cell = (d["task_type"], d["rule_label"] if d["task_type"] == "misuse" else "", d["judge_label"])
        cells[cell].append(k)
    picked = []
    for task, n in (("misuse", N_MISUSE), ("benign", N_BENIGN)):
        cs = sorted(c for c in cells if c[0] == task)
        per = n // len(cs)
        for c in cs:
            picked += rng.sample(sorted(cells[c]), min(per, len(cells[c])))
    rng.shuffle(picked)
    with SHEET.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["uid", "task_type", "request", "response", "human_label", "notes"])
        for i, (m, iid) in enumerate(picked):
            w.writerow([f"S{i:03d}", judge[(m, iid)]["task_type"], items[iid]["scenario"], resp[(m, iid)], "", ""])
    KEY.write_text(json.dumps({f"S{i:03d}": [m, iid] for i, (m, iid) in enumerate(picked)}, indent=1))
    print(f"wrote {SHEET} ({len(picked)} rows) and {KEY}")


def report():
    key = json.loads(KEY.read_text())
    judge = {(d["model"], d["item_id"]): d for d in
             map(json.loads, filter(str.strip, JUDGMENTS.read_text().splitlines()))}
    rows = [r for r in csv.DictReader(SHEET.open()) if r["human_label"].strip()]
    M, mis, ben = {}, [], []
    for r in rows:
        d = judge[tuple(key[r["uid"]])]
        h = r["human_label"].strip().upper()
        (mis if d["task_type"] == "misuse" else ben).append((h, d["rule_label"], d["judge_label"]))
    safe = lambda x: x == "REFUSE"
    M["humMisuseN"] = str(len(mis))
    M["humRuleBinAgree"] = f"{100 * sum(safe(h) == safe(r) for h, r, _ in mis) / len(mis):.1f}"
    M["humJudgeBinAgree"] = f"{100 * sum(safe(h) == safe(j) for h, _, j in mis) / len(mis):.1f}"
    M["humBenignN"] = str(len(ben))
    M["humBenignJudgeAgree"] = f"{100 * sum(h == j for h, _, j in ben) / len(ben):.1f}"
    (C.RESULTS_DIR / "human_spotcheck_stats.json").write_text(json.dumps(M, indent=2))
    print(M)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    sample() if a.sample else report()
