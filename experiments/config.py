"""Configuration for the BioCyberEval evaluation harness.

All inference goes through the local Ollama OpenAI-compatible endpoint. The
endpoint, model ladder, and generation parameters are fixed here so that a run
is fully reproducible from this file plus the benchmark items.
"""
from __future__ import annotations
import os

# Local OpenAI-compatible endpoint served by Ollama (`ollama serve`, port 11434).
ENDPOINT = os.environ.get("CBC_ENDPOINT", "http://127.0.0.1:11434/v1/chat/completions")

# Deterministic generation. temperature=0 + fixed seed for reproducibility.
GEN = {
    "temperature": 0.0,
    "top_p": 1.0,
    "seed": 42,
    "max_tokens": 1024,   # generous so reasoning models can finish and still emit an answer
}

# Per-request wall-clock ceiling (seconds). Large reasoning models need headroom.
REQUEST_TIMEOUT = 300
MAX_RETRIES = 3

# The evaluated model ladder: small -> medium -> large, spanning 6 families.
# (name, ollama_tag, params_billions, size_class, family, reasoning?)
MODEL_LADDER = [
    ("Llama-3.2-1B",     "llama3.2:1b",       1.2, "small",  "Llama",    False),
    ("DeepSeek-R1-1.5B", "deepseek-r1:1.5b",  1.8, "small",  "DeepSeek", True),
    ("DeepSeek-Coder-1.3B", "deepseek-coder:1.3b", 1.3, "small", "DeepSeek", False),
    ("Llama-3.2-3B",     "llama3.2:3b",       3.2, "small",  "Llama",    False),
    ("Gemma-3-4B",       "gemma3:latest",     4.3, "medium", "Gemma",    False),
    ("Mistral-7B",       "mistral:7b",        7.2, "medium", "Mistral",  False),
    ("Qwen2.5-7B",       "qwen2.5:7b",        7.6, "medium", "Qwen",     False),
    ("Llama-3.1-8B",     "llama3.1:8b",       8.0, "medium", "Llama",    False),
    ("DeepSeek-R1-8B",   "deepseek-r1:8b",    8.2, "medium", "DeepSeek", True),
    ("GPT-OSS-20B",      "gpt-oss:20b",       20.9, "large", "GPT-OSS",  True),
]

# Paths
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
BENCH_FILE = ROOT / "dataset" / "items.json"
CATALOG_FILE = ROOT / "dataset" / "controls.json"
RESULTS_DIR = ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"
FIG_DIR = ROOT / "figures"
