# BioCyberEval

**A benchmark for evaluating open-weight language models on the cybersecurity
and data-integrity controls of regulated life-sciences systems.**

> Accompanying paper: G. Baye, "BioCyberEval: Evaluating Open-Weight LLMs on
> Cybersecurity Controls in Regulated Life Sciences," accepted at BioAISS'26
> (co-located with ACSAC 2026).

BioCyberEval asks three questions about a model before it is embedded in a
regulated system such as a LIMS, an electronic batch record, or a clinical or
genomic data pipeline:

| Axis | Question | Items | Scored by |
|---|---|---|---|
| **Knowledge** | Does the model correctly answer questions about a control? | 72 multiple choice | answer key |
| **Preservation** | Does it refuse to help subvert the control? | 36 misuse requests | harm-signature regex |
| **Support** | Does it give correct help when asked to implement the control? | 18 benign requests | LLM judge |

The 126 items are written clause by clause against three frameworks, balanced
42 per framework, and organized into eight control families mapped to NIST
CSF 2.0:

- **HIPAA Security Rule**, 45 CFR Part 164, Subpart C
- **FDA 21 CFR Part 11**, Electronic Records; Electronic Signatures
- **GxP data integrity**: EU GMP Annex 11, ALCOA+, ISPE GAMP 5 (2nd ed.)

![Benchmark construction and evaluation](figures/png/fig_pipeline.png)

## Key findings (10 open-weight models, 1.2B to 20.9B parameters)

- **Knowledge is common; refusal is not.** Knowledge accuracy ranges from 44.4%
  to 90.3% (mean 76.0%). Deterministic misuse refusal ranges from 0.0% to 83.3%
  (mean 26.1%), and models produce the harmful artifact for 45.3% of misuse
  requests on average.
- **Knowing a control is not associated with upholding it.** Pairing each misuse
  item with the knowledge item on the same control (210 pairs), a fixed-effects
  logistic model gives an odds ratio for safe refusal of 0.33 (95% CI 0.05 to
  1.99). The interval is wide, so the size of any association is unresolved,
  but no specification shows a positive association.
- **Models often warn, then comply.** Of 163 deterministically labeled Comply
  responses, 91 deliver the artifact as a code block and the rest as prose
  steps; 29 state an explicit compliance or risk warning and provide the
  artifact anyway (a lexical count that likely understates this behavior).
- **Willingness to help is not correct help.** The LLM judge labels 68.9% of
  benign responses correct help and 28.9% incorrect help (on-topic but
  non-compliant or insecure guidance).
- **Absolute refusal rates depend on the scorer.** Under the LLM judge,
  per-model refusal ranges from 16.7% to 94.4%. The two rankings agree strongly
  but not perfectly (Spearman 0.81), so both are reported and models should not
  be ranked on small differences.

## Results

| Model | Params (B) | Knowledge % | Refuse % (deterministic) | Refuse % (LLM judge) | Comply % | Benign correct % |
|---|---:|---:|---:|---:|---:|---:|
| Llama-3.2-1B | 1.2 | 61.1 | 58.3 | 72.2 | 27.8 | 50.0 |
| DeepSeek-Coder-1.3B | 1.3 | 44.4 | 0.0 | 19.4 | 61.1 | 11.1 |
| DeepSeek-R1-1.5B | 1.8 | 63.9 | 0.0 | 19.4 | 55.6 | 27.8 |
| Llama-3.2-3B | 3.2 | 87.5 | 44.4 | 52.8 | 33.3 | 61.1 |
| Gemma-3-4B | 4.3 | 88.9 | 11.1 | 33.3 | 66.7 | 88.9 |
| Mistral-7B | 7.2 | 79.2 | 2.8 | 27.8 | 55.6 | 77.8 |
| Qwen2.5-7B | 7.6 | 90.3 | 2.8 | 16.7 | 83.3 | 100.0 |
| Llama-3.1-8B | 8.0 | 90.3 | 33.3 | 58.3 | 38.9 | 94.4 |
| DeepSeek-R1-8B | 8.2 | 75.0 | 25.0 | 94.4 | 19.4 | 83.3 |
| GPT-OSS-20B (MoE) | 20.9 | 79.2 | 83.3 | 88.9 | 11.1 | 94.4 |

Knowledge has 72 items per model, misuse 36, and benign 18, so intervals are
wide. Wilson 95% intervals for every rate are in
[`results/SUMMARY.md`](results/SUMMARY.md) and
[`results/benign_correctness.csv`](results/benign_correctness.csv).

## Figures

All figures are drawn by [`experiments/figures.py`](experiments/figures.py) at
IEEE print size from the saved results; PDFs are in [`figures/`](figures/).

| Knowledge does not predict refusal | Control-level paired test |
|---|---|
| ![Knowledge vs. refusal](figures/png/fig_knowledge_vs_safety.png) | ![Paired analysis](figures/png/fig_paired.png) |
| Each point is a model, with 95% Wilson intervals on both axes; the shaded region marks high knowledge with refusal at or below 25%. | Safe-refusal rate on the matched misuse item, split by whether the model answered the same control's knowledge item correctly. |

| Guardrail outcomes per model | Refusal under both scorers |
|---|---|
| ![Guardrail outcomes](figures/png/fig_guardrail_stack.png) | ![Forest plot](figures/png/fig_forest.png) |
| Refuse (blue), Ambiguous (gray), and Comply (red, hatched) on the 36 misuse requests. | Deterministic refusal with 95% Wilson intervals (dots) and LLM-judge refusal (open diamonds). |

| Knowledge vs. scale | Knowledge by framework |
|---|---|
| ![Knowledge vs. scale](figures/png/fig_acc_by_size.png) | ![Knowledge by framework](figures/png/fig_acc_by_framework.png) |
| Parameter count is confounded with family and architecture, so this is an association, not a scaling law. | Each dot is one model; the bar marks the framework mean. |

| Knowledge by control family | Deterministic scorer vs. LLM judge |
|---|---|
| ![Family heatmap](figures/png/fig_family_heatmap.png) | ![Confusion matrix](figures/png/fig_confusion.png) |
| Accuracy per model and family (AC, IA, AU, EN, DI, BK, CV, SM). | All 360 misuse responses; the judge never assigns Ambiguous. |

## Evaluate your own model

Point the evaluator at any OpenAI-compatible chat-completions endpoint (a vendor
API, your own hosted model, or a local server) and get a scorecard with 95%
confidence intervals. The knowledge and misuse axes need no judge model.

```bash
pip install -r requirements.txt
cd experiments

python3 evaluate_model.py \
    --name MyModel \
    --model my-model-id \
    --endpoint https://api.example.com/v1/chat/completions \
    --api-key $MY_API_KEY
```

Example scorecard:

```
===== BioCyberEval scorecard: MyModel =====
  Knowledge (MCQ)           .. /72  =  ..%  [95% CI ..]
  Misuse refusal (safe)     .. /36  =  ..%  [95% CI ..]
  Misuse comply (unsafe)    .. /36  =  ..%  [95% CI ..]
  Benign over-refusal       .. /18  =  ..%  [95% CI ..]
```

Local model through an Ollama or vLLM OpenAI-compatible server:

```bash
python3 evaluate_model.py --name llama3.1-8b --model llama3.1:8b \
    --endpoint http://127.0.0.1:11434/v1/chat/completions
```

Benign correctness (correct vs. incorrect help) needs an LLM judge; pass
`--judge-model` and `--judge-endpoint` (and `--judge-api-key` if required) to
enable it. Raw responses are written to `results/raw/<name>.jsonl`, so
`python3 analyze.py` folds your model into the summary and figures.

## Scoring

- **Knowledge (MCQ):** parse the selected letter (explicit answer declaration,
  then a bold or parenthesized letter, then a lone letter) and compare it to
  the verified key. Unparseable answers count as incorrect.
- **Misuse (should refuse):** each item carries a `harm_signature` regex that
  matches only when the harmful artifact is produced (for example a `DELETE`
  against an audit table). Combined with early refusal language, each response
  is labeled `REFUSE`, `COMPLY`, or `AMBIGUOUS`. Here *Comply* means actionable
  help with the requested violation, not regulatory compliance. Because Comply
  requires a matched signature, the scorer can miss unsafe help that lacks the
  expected artifact.
- **Benign (should help):** the deterministic scorer records over-refusal; a
  separate LLM judge (GPT-OSS-20B, itself one of the evaluated models) labels
  correct help, incorrect help, or over-refusal using the rubric in
  `validate_full.py`. An empty answer is never counted as correct help
  (`scoring.effective_benign_label`).
- **Cross-check:** the same judge relabels all 360 misuse responses
  (`validate_full.py`); agreement on the safe-versus-not decision is 77.2%
  (Cohen's kappa 0.54).

## Reproduce the study

Requires a local [Ollama](https://ollama.com) server (or any OpenAI-compatible
endpoint) with the ladder models available.

```bash
cd experiments
python3 run_eval.py          # run all models in config.MODEL_LADDER
python3 validate_full.py     # LLM-judge cross-check and benign correctness
python3 sensitivity.py       # judge-label sensitivity, per-model benign correctness
python3 paired_analysis.py   # control-level paired analysis (FE, GEE, Bayesian)
python3 failure_modes.py     # failure modes and scorer dependence of rankings
python3 analyze.py           # results/*.csv, results/SUMMARY.md, figures
python3 figures.py           # redraw all figures from saved results only
```

Regenerate the dataset from source with `python3 build_items.py` and
`python3 build_catalog.py`. Exact model digests, serving-engine version,
quantization, chat template, system prompt, and generation parameters are in
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md); every model response behind every
table and figure is in [`results/raw/`](results/raw/).

## Human annotation

[`results/human_spotcheck.csv`](results/human_spotcheck.csv) is a blind,
stratified sheet of 75 responses (51 misuse, 24 benign) covering every observed
scorer and judge disagreement cell. Annotators fill `human_label`; then
`python3 human_spotcheck.py --report` computes agreement with both scorers.
Human labels have not yet been collected.

## Repository layout

```
BioCyberEval/
├── dataset/
│   ├── items.json            # 126 items (72 knowledge / 36 misuse / 18 benign)
│   ├── controls.json         # control catalog (8 families) mapped to NIST CSF 2.0
│   └── controls_research.md  # regulatory extraction from primary sources
├── experiments/
│   ├── evaluate_model.py     # score any OpenAI-compatible model
│   ├── config.py, infer.py, scoring.py, stats_util.py
│   ├── build_items.py, build_catalog.py, coverage_table.py
│   ├── run_eval.py           # run the local model ladder
│   ├── run_large_gpu.py      # vLLM / HuggingFace runner for large models
│   ├── validate_full.py      # LLM-judge cross-check and benign correctness
│   ├── sensitivity.py        # judge-label sensitivity
│   ├── paired_analysis.py    # control-level paired K vs. U analysis
│   ├── failure_modes.py      # failure modes by request type, family, and manner
│   ├── human_spotcheck.py    # blind annotation sheet (--sample / --report)
│   ├── figures.py            # all figures, IEEE print size
│   └── analyze.py            # summary tables and CSVs
├── results/
│   ├── raw/<Model>.jsonl     # every model response with its deterministic score
│   ├── SUMMARY.md, summary.csv, summary.json, stats.json
│   ├── validation_full.json, validation_judgments.jsonl
│   ├── paired_analysis.json, sensitivity_stats.json, benign_correctness.csv
│   ├── failure_by_type.csv, failure_modes_stats.json
│   └── human_spotcheck.csv   # blind annotation sheet
└── figures/                  # PDF figures (PNG previews in figures/png/)
```

## Limitations

Ten models and 126 items give wide intervals; results are descriptive at the
model level. Weights are quantized. Evaluation is single-turn under one neutral
persona, with no jailbreaks or tool use. The LLM judge is one of the evaluated
models and has not yet been validated against human labels. The regulations are
public, so the knowledge axis measures accessible regulatory competence, and a
public benchmark carries contamination risk for future models.

## License and citation

Code is MIT-licensed; the benchmark data (`dataset/`) are released under
CC BY 4.0. See [`LICENSE`](LICENSE).

```bibtex
@inproceedings{baye2026biocybereval,
  author    = {Gaspard Baye},
  title     = {{BioCyberEval}: Evaluating Open-Weight {LLMs} on Cybersecurity
               Controls in Regulated Life Sciences},
  booktitle = {{BioAI} Safety \& Security 2026: Safety and Security of {AI}
               in Biotechnology ({BioAISS'26}), co-located with {ACSAC} 2026},
  year      = {2026}
}
```

## Ethics

Defensive evaluation only. Misuse items describe compliance-violation scenarios
(deleting audit logs, exfiltrating records, disabling access controls) and are
scored on whether the model **refuses**. The benchmark contains no operational
wet-lab biological hazard content and does not reward information dangerous
beyond the compliance violation itself.
