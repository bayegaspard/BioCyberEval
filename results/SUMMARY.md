# BioCyberEval results

Per-model knowledge and guardrail results (10 open-weight models).
MCQ = compliance-knowledge accuracy (72 items); Refuse/Comply = guardrail
outcome on 36 misuse items; brackets are 95% Wilson intervals. Deterministic
scoring, temperature 0.

| Model | Size (B) | Family | MCQ % [95% CI] | Refuse % [95% CI] | Comply % [95% CI] |
|---|---|---|---|---|---|
| Llama-3.2-1B | 1.2 | Llama | 61.1 [49.6-71.5] | 58.3 [42.2-72.9] | 27.8 [15.8-44.0] |
| DeepSeek-R1-1.5B | 1.8 | DeepSeek | 63.9 [52.4-74.0] | 0.0 [0.0-9.6] | 55.6 [39.6-70.5] |
| DeepSeek-Coder-1.3B | 1.3 | DeepSeek | 44.4 [33.5-55.9] | 0.0 [0.0-9.6] | 61.1 [44.9-75.2] |
| Llama-3.2-3B | 3.2 | Llama | 87.5 [77.9-93.3] | 44.4 [29.5-60.4] | 33.3 [20.2-49.7] |
| Gemma-3-4B | 4.3 | Gemma | 88.9 [79.6-94.3] | 11.1 [4.4-25.3] | 66.7 [50.3-79.8] |
| Mistral-7B | 7.2 | Mistral | 79.2 [68.4-86.9] | 2.8 [0.5-14.2] | 55.6 [39.6-70.5] |
| Qwen2.5-7B | 7.6 | Qwen | 90.3 [81.3-95.2] | 2.8 [0.5-14.2] | 83.3 [68.1-92.1] |
| Llama-3.1-8B | 8.0 | Llama | 90.3 [81.3-95.2] | 33.3 [20.2-49.7] | 38.9 [24.8-55.1] |
| DeepSeek-R1-8B | 8.2 | DeepSeek | 75.0 [63.9-83.6] | 25.0 [13.8-41.1] | 19.4 [9.8-35.0] |
| GPT-OSS-20B | 20.9 | GPT-OSS | 79.2 [68.4-86.9] | 83.3 [68.1-92.1] | 11.1 [4.4-25.3] |

## Key statistics

- Models: 10; items: 126 (72 knowledge / 36 misuse / 18 benign).
- Knowledge (MCQ): mean 76.0%, range 44.4-90.3%.
- Misuse refusal: mean 26.1%, range 0.0-83.3%; mean comply 45.3%.
- Knowledge vs scale: Pearson r=0.68 (p=0.030); Spearman rho=0.55 (p=0.100); dense-only r=0.79.
- Knowledge vs refusal (model level): Pearson r=0.14, 95% CI [-0.54, 0.71], p=0.696.
- Framework means: HIPAA 71.7%, Part 11 75.0%, GxP 81.2%.
- Weakest control families: EN, AC; strongest: BK, DI, AU.
- Control-level paired K-vs-U analysis: results/paired_analysis.json.
- Scorer cross-check vs independent judge: results/validation_full.json.
- Benign correctness (judge-based): results/benign_correctness.csv (from sensitivity.py).
