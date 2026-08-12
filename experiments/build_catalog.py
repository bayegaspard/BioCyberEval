"""Emit catalog/controls.json: the normalized cyber-control taxonomy, the NIST
CSF 2.0 crosswalk, and the benchmark's coverage of each family/framework
(computed from benchmark/items.json so the catalog and benchmark stay in sync).

Regulatory control text is transcribed from primary sources (45 CFR 164.3xx;
21 CFR 11.x; EU GMP Annex 11) as verified in catalog/controls_research.md.
"""
import json, pathlib
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
ITEMS = json.loads((ROOT / "dataset" / "items.json").read_text())
OUT = ROOT / "dataset" / "controls.json"

FAMILIES = {
    "AC": {"name": "Access Control & Authorization",
           "csf_functions": ["Protect"], "csf_categories": ["PR.AA"]},
    "IA": {"name": "Identity & Authentication",
           "csf_functions": ["Protect", "Govern"], "csf_categories": ["PR.AA", "GV.RR"]},
    "AU": {"name": "Audit Trail & Logging",
           "csf_functions": ["Detect", "Protect"], "csf_categories": ["DE.CM", "DE.AE", "PR.PS"]},
    "EN": {"name": "Encryption & Transmission Security",
           "csf_functions": ["Protect"], "csf_categories": ["PR.DS"]},
    "DI": {"name": "Data Integrity & Non-repudiation",
           "csf_functions": ["Protect", "Detect"], "csf_categories": ["PR.DS", "DE.CM"]},
    "BK": {"name": "Backup, Availability & Contingency",
           "csf_functions": ["Recover", "Protect"], "csf_categories": ["RC.RP", "PR.IR"]},
    "CV": {"name": "Configuration, Validation & Change Control",
           "csf_functions": ["Protect", "Identify"], "csf_categories": ["PR.PS", "ID.AM", "ID.RA"]},
    "SM": {"name": "Security Management, Risk & Incident Response",
           "csf_functions": ["Govern", "Identify", "Respond"], "csf_categories": ["GV.RM", "ID.RA", "RS.MA"]},
}
NAME_TO_CODE = {v["name"]: k for k, v in FAMILIES.items()}

FRAMEWORKS = {
    "HIPAA": {"name": "HIPAA Security Rule",
              "authority": "45 CFR Part 164, Subpart C (US)",
              "scope": "Confidentiality, integrity, availability of electronic PHI (ePHI).",
              "authoritative_source": "https://www.ecfr.gov/current/title-45/part-164/subpart-C"},
    "Part11": {"name": "FDA 21 CFR Part 11",
               "authority": "21 CFR Part 11 (US)",
               "scope": "Trustworthiness of electronic records and electronic signatures in FDA-regulated activities.",
               "authoritative_source": "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11"},
    "GxP": {"name": "GxP data integrity (EU GMP Annex 11, ALCOA+, ISPE GAMP 5)",
            "authority": "EudraLex Vol. 4 Annex 11 (EU); ALCOA+ (FDA/MHRA/PIC/S); ISPE GAMP 5 2nd ed.",
            "scope": "Data integrity and security of GxP computerised systems across the lifecycle.",
            "authoritative_source": "https://health.ec.europa.eu/system/files/2016-11/annex11_01-2011_en_0.pdf"},
}

# Representative cyber controls per framework (verified against primary text).
CONTROLS = [
    # HIPAA technical safeguards
    ("HIPAA-312-a-1","HIPAA","45 CFR 164.312(a)(1)","Access control","Standard","AC"),
    ("HIPAA-312-a-2-i","HIPAA","45 CFR 164.312(a)(2)(i)","Unique user identification","Required","IA"),
    ("HIPAA-312-a-2-ii","HIPAA","45 CFR 164.312(a)(2)(ii)","Emergency access procedure","Required","AC"),
    ("HIPAA-312-a-2-iii","HIPAA","45 CFR 164.312(a)(2)(iii)","Automatic logoff","Addressable","AC"),
    ("HIPAA-312-a-2-iv","HIPAA","45 CFR 164.312(a)(2)(iv)","Encryption and decryption (at rest)","Addressable","EN"),
    ("HIPAA-312-b","HIPAA","45 CFR 164.312(b)","Audit controls","Standard","AU"),
    ("HIPAA-312-c-1","HIPAA","45 CFR 164.312(c)(1)","Integrity","Standard","DI"),
    ("HIPAA-312-c-2","HIPAA","45 CFR 164.312(c)(2)","Mechanism to authenticate ePHI","Addressable","DI"),
    ("HIPAA-312-d","HIPAA","45 CFR 164.312(d)","Person or entity authentication","Standard","IA"),
    ("HIPAA-312-e-1","HIPAA","45 CFR 164.312(e)(1)","Transmission security","Standard","EN"),
    ("HIPAA-312-e-2-ii","HIPAA","45 CFR 164.312(e)(2)(ii)","Encryption (in transit)","Addressable","EN"),
    ("HIPAA-308-a-1-ii-A","HIPAA","45 CFR 164.308(a)(1)(ii)(A)","Risk analysis","Required","SM"),
    ("HIPAA-308-a-1-ii-D","HIPAA","45 CFR 164.308(a)(1)(ii)(D)","Information system activity review","Required","AU"),
    ("HIPAA-308-a-4-i","HIPAA","45 CFR 164.308(a)(4)(i)","Information access management","Standard","AC"),
    ("HIPAA-308-a-5-ii-D","HIPAA","45 CFR 164.308(a)(5)(ii)(D)","Password management","Addressable","IA"),
    ("HIPAA-308-a-6-ii","HIPAA","45 CFR 164.308(a)(6)(ii)","Security incident response and reporting","Required","SM"),
    ("HIPAA-308-a-7-ii-A","HIPAA","45 CFR 164.308(a)(7)(ii)(A)","Data backup plan","Required","BK"),
    ("HIPAA-310-d-1","HIPAA","45 CFR 164.310(d)(1)","Device and media controls","Standard","SM"),
    # 21 CFR Part 11
    ("PART11-11.10-a","Part11","21 CFR 11.10(a)","System validation","Mandatory","CV"),
    ("PART11-11.10-b","Part11","21 CFR 11.10(b)","Accurate and complete copies","Mandatory","BK"),
    ("PART11-11.10-c","Part11","21 CFR 11.10(c)","Record protection and retrieval","Mandatory","BK"),
    ("PART11-11.10-d","Part11","21 CFR 11.10(d)","Limiting system access","Mandatory","AC"),
    ("PART11-11.10-e","Part11","21 CFR 11.10(e)","Secure computer-generated time-stamped audit trails","Mandatory","AU"),
    ("PART11-11.10-f","Part11","21 CFR 11.10(f)","Operational system checks","Mandatory","CV"),
    ("PART11-11.10-g","Part11","21 CFR 11.10(g)","Authority checks","Mandatory","AC"),
    ("PART11-11.10-h","Part11","21 CFR 11.10(h)","Device checks","Mandatory","IA"),
    ("PART11-11.10-k","Part11","21 CFR 11.10(k)","Controls over systems documentation","Mandatory","CV"),
    ("PART11-11.30","Part11","21 CFR 11.30","Open-system controls (encryption, digital signatures)","Mandatory","EN"),
    ("PART11-11.50","Part11","21 CFR 11.50","Signature manifestations","Mandatory","DI"),
    ("PART11-11.70","Part11","21 CFR 11.70","Signature/record linking","Mandatory","DI"),
    ("PART11-11.100-a","Part11","21 CFR 11.100(a)","Signature uniqueness","Mandatory","IA"),
    ("PART11-11.200-a","Part11","21 CFR 11.200(a)","Non-biometric signature components/controls","Mandatory","IA"),
    ("PART11-11.300-a","Part11","21 CFR 11.300(a)","Credential (ID code/password) uniqueness","Mandatory","IA"),
    ("PART11-11.300-b","Part11","21 CFR 11.300(b)","Periodic credential revision (aging)","Mandatory","IA"),
    ("PART11-11.300-c","Part11","21 CFR 11.300(c)","Credential loss management","Mandatory","IA"),
    ("PART11-11.300-d","Part11","21 CFR 11.300(d)","Transaction safeguards (detect/report misuse)","Mandatory","SM"),
    # GxP Annex 11 / ALCOA+ / GAMP 5
    ("ANNEX11-4","GxP","EU GMP Annex 11 cl.4","Validation","Mandatory","CV"),
    ("ANNEX11-5","GxP","EU GMP Annex 11 cl.5","Secure data entry and processing","Mandatory","DI"),
    ("ANNEX11-6","GxP","EU GMP Annex 11 cl.6","Accuracy checks","Mandatory","DI"),
    ("ANNEX11-7","GxP","EU GMP Annex 11 cl.7","Data storage and backups","Mandatory","BK"),
    ("ANNEX11-9","GxP","EU GMP Annex 11 cl.9","Audit trails","Mandatory","AU"),
    ("ANNEX11-10","GxP","EU GMP Annex 11 cl.10","Change and configuration management","Mandatory","CV"),
    ("ANNEX11-12","GxP","EU GMP Annex 11 cl.12","Security / access restriction","Mandatory","AC"),
    ("ANNEX11-12-4","GxP","EU GMP Annex 11 cl.12.4","Operator identity capture","Mandatory","AU"),
    ("ANNEX11-14","GxP","EU GMP Annex 11 cl.14","Electronic signature","Mandatory","DI"),
    ("ANNEX11-16","GxP","EU GMP Annex 11 cl.16","Business continuity","Mandatory","BK"),
    ("ANNEX11-17","GxP","EU GMP Annex 11 cl.17","Archiving","Mandatory","BK"),
    ("ALCOA","GxP","ALCOA+ (FDA/MHRA/PIC-S)","ALCOA+ data-integrity principles","Principle","DI"),
    ("GAMP5-D11","GxP","ISPE GAMP 5 2nd ed. App. D11","Risk-based AI/ML lifecycle validation","Guidance","CV"),
]

controls = [{"control_id": c[0], "framework": c[1], "citation": c[2],
             "title": c[3], "obligation": c[4],
             "family": c[5], "family_name": FAMILIES[c[5]]["name"]} for c in CONTROLS]

# Benchmark coverage computed from real items
cov_family = defaultdict(lambda: Counter())
cov_task = defaultdict(lambda: Counter())
for it in ITEMS:
    code = NAME_TO_CODE[it["control_family"]]
    cov_family[it["framework"]][code] += 1
    cov_task[it["framework"]][it["task_type"]] += 1

coverage = {
    "n_items": len(ITEMS),
    "by_framework_family": {fw: dict(cov_family[fw]) for fw in FRAMEWORKS},
    "by_framework_task": {fw: dict(cov_task[fw]) for fw in FRAMEWORKS},
    "family_totals": dict(Counter(NAME_TO_CODE[i["control_family"]] for i in ITEMS)),
}

catalog = {
    "name": "BioCyberEval control catalog",
    "version": "1.0",
    "families": FAMILIES,
    "frameworks": FRAMEWORKS,
    "controls": controls,
    "benchmark_coverage": coverage,
    "notes": ("Regulatory text verified against primary sources (Cornell LII "
              "mirror of eCFR; EC EudraLex Annex 11 PDF). Family and CSF 2.0 "
              "assignments are analytical. GAMP 5 App. D11 paraphrased from "
              "ISPE public ToC/commentary (paywalled guide)."),
}

OUT.write_text(json.dumps(catalog, indent=2))
print(f"wrote {OUT} with {len(controls)} controls, {coverage['n_items']} benchmark items")
print("family totals:", coverage["family_totals"])
