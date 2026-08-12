"""Emit COVERAGE.md: framework x control-family x task-type coverage of the
benchmark, so a reviewer can inspect balance. K/M/B = knowledge / misuse / benign."""
import json, pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
items = json.loads((ROOT / "dataset" / "items.json").read_text())
FAMS = ["AC", "IA", "AU", "EN", "DI", "BK", "CV", "SM"]
NAME = {"Access Control & Authorization": "AC", "Identity & Authentication": "IA",
        "Audit Trail & Logging": "AU", "Encryption & Transmission Security": "EN",
        "Data Integrity & Non-repudiation": "DI", "Backup, Availability & Contingency": "BK",
        "Configuration, Validation & Change Control": "CV",
        "Security Management, Risk & Incident Response": "SM"}
TT = {"mcq": "K", "misuse": "M", "benign": "B"}
FWS = ["HIPAA", "Part11", "GxP"]

cell = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # fw -> fam -> tt -> n
for it in items:
    cell[it["framework"]][NAME[it["control_family"]]][TT[it["task_type"]]] += 1

out = ["# Benchmark coverage (framework x control family x task type)", "",
       "Each cell is K/M/B = knowledge / misuse / benign item counts.", "",
       "| Framework | " + " | ".join(FAMS) + " | Total |",
       "|" + "---|" * (len(FAMS) + 2)]
gtot = 0
for fw in FWS:
    row = [fw]
    fwtot = 0
    for fam in FAMS:
        c = cell[fw][fam]
        n = c["K"] + c["M"] + c["B"]; fwtot += n
        row.append(f'{c["K"]}/{c["M"]}/{c["B"]}' if n else "-")
    gtot += fwtot
    row.append(str(fwtot))
    out.append("| " + " | ".join(row) + " |")
out += ["", f"Total items: {gtot} (72 knowledge, 36 misuse, 18 benign)."]
(ROOT / "results" / "coverage.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
