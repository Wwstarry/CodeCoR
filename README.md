<div align="center">

# CodeCoR 🤖🔧

### An LLM-Based Self-Reflective Multi-Agent Framework for Code Generation

[![arXiv](https://img.shields.io/badge/arXiv-2501.07811-b31b1b.svg)](https://arxiv.org/abs/2501.07811)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![evalplus](https://img.shields.io/badge/benchmark-evalplus-green)](https://github.com/evalplus/evalplus)

> **TL;DR:** CodeCoR is a self-reflective multi-agent system that generates, tests, and iteratively repairs code using four specialized LLM agents, achieving **86.6% Pass@1 on HumanEval** and **79.2% on MBPP** with GPT-3.5-turbo—outperforming MapCoder (80.5% / 78.9%) and all prior multi-agent frameworks.

</div>

---

## 🔍 Overview

Standard multi-agent code generation pipelines are brittle: a single poor decision by one agent propagates errors to every downstream agent. **CodeCoR** addresses this with a *self-reflective* architecture that:

1. **Generates diverse candidates** at each phase (CoT prompts, test cases, code snippets)
2. **Prunes low-quality outputs** before they contaminate downstream agents
3. **Iteratively repairs failures** using execution feedback and targeted advice
4. **Ranks all candidates** by execution results and returns the best one

```
Task Description
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase I  │  Prompt Agent  │ generate N CoT prompts → prune     │
├─────────────────────────────────────────────────────────────────┤
│  Phase II │  Test Agent    │ generate M test cases  → prune     │
├─────────────────────────────────────────────────────────────────┤
│  Phase III│  Coding Agent  │ generate K code snippets → prune   │
├─────────────────────────────────────────────────────────────────┤
│  Phase IV │  Executor      │ run code vs. tests                  │
│           │                │   ┌──pass──► Ranked Code Set        │
│           │                │   └──fail──► Repair Queue           │
├─────────────────────────────────────────────────────────────────┤
│  Phase V  │  Repair Agent  │ advice → Coding Agent → re-execute  │
│           │  (≤ 3 rounds)  │   (loop until pass or no progress)  │
└─────────────────────────────────────────────────────────────────┘
      │
      ▼
  Highest-Ranked Code  (most tests passed, fewest repair rounds)
```

**Pruning criteria** (for Prompt Agent and Repair Agent outputs):

| Score | Criterion | Meaning |
|:---:|---|---|
| **Clarity** | 0 / 1 | Output is clear and unambiguous |
| **Relevance** | 0 / 1 | Directly addresses the task |
| **Conciseness** | 0 / 1 | Not overly verbose or complex |
| **Context** | 0 / 1 | Provides sufficient contextual information |

An output must score **[1, 1, 1, 1]** to survive pruning.

---

## 📊 Results

### Pass@1 on HumanEval and MBPP (GPT-3.5-turbo backend)

| Method | HumanEval | HumanEval-ET | MBPP | MBPP-ET | **Avg** |
|---|:---:|:---:|:---:|:---:|:---:|
| Few-Shot | 67.7 | 54.9 | 65.8 | 48.3 | 59.2 |
| Reflexion | 68.1 | 50.6 | 70.0 | 47.4 | 59.0 |
| Self-Collaboration | 74.4 | 56.1 | 68.2 | 49.5 | 62.1 |
| INTERVENOR | 75.6 | 54.8 | 69.8 | 47.1 | 61.8 |
| CodeCoT | 79.3 | 69.5 | 67.7 | 58.1 | 68.7 |
| MapCoder | 80.5 | 77.4 | 78.9 | 54.4 | 72.8 |
| **CodeCoR (ours)** | **86.6** | **80.5** | **79.2** | **65.2** | **77.8** |

### Pass@1 with Other LLM Backends (HumanEval)

| Method | GPT-4 | CodeLlama-34B |
|---|:---:|:---:|
| MapCoder | 93.9 | 42.7 |
| **CodeCoR (ours)** | **94.5** | **43.9** |

### Code Quality Metrics (HumanEval)

| Method | Avg Edit Distance ↓ | Avg BLEU ↑ |
|---|:---:|:---:|
| Self-Planning | 387.53 | 0.249 |
| CodeChain | 357.20 | 0.263 |
| MapCoder | 396.20 | 0.236 |
| **CodeCoR (ours)** | **378.79** | **0.276** |

---

## 🚀 Installation

### Requirements

- Python ≥ 3.9
- An LLM API key: [Anthropic Claude](https://www.anthropic.com/) **or** [OpenAI](https://platform.openai.com/)

### Install

```bash
git clone https://github.com/panruwei/CodeCoR.git
cd CodeCoR

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Set API Keys

**Option A — OpenAI (reproduces paper's exact results):**
```bash
export OPENAI_API_KEY=sk-...
```

**Option B — Native Anthropic:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**Option C — OpenAI-compatible proxy for Claude (enterprise / internal deployments):**
```bash
# Many enterprises expose Claude via an OpenAI-compatible proxy endpoint.
# Use --backend openai with your proxy's URL and key.
export OPENAI_API_KEY=YOUR_INTERNAL_KEY
export OPENAI_BASE_URL=https://your-proxy.example.com/v1
```

---

## ⚡ Quick Start

```python
from codecor import CodeCoR, CodeCoRConfig, LLMClient

# Initialize LLM client (Anthropic or OpenAI)
llm = LLMClient(backend="anthropic", model="claude-haiku-4-5-20251001")

# Initialize CodeCoR framework
framework = CodeCoR(llm)

# Solve a coding problem
task = """
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    \"\"\"Check if any two numbers in the list are closer than threshold.\"\"\"
"""

solution = framework.generate(task)
print(solution)
```

**Output:**
```python
def has_close_elements(numbers, threshold):
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if abs(numbers[i] - numbers[j]) < threshold:
                return True
    return False
```

### Command-Line Demo

```bash
# Default: Anthropic Claude Haiku
python examples/demo.py

# GPT-3.5-turbo (paper's primary model)
python examples/demo.py --backend openai --model gpt-3.5-turbo

# Custom problem
python examples/demo.py --problem "Write a function that reverses a linked list."
```

---

## 📖 Usage

### HumanEval Evaluation

```bash
# Step 1: Generate solutions (all 164 problems)
python evaluate/run_humaneval.py \
    --backend anthropic \
    --model claude-haiku-4-5-20251001 \
    --output results/humaneval_claude.jsonl

# Step 2: Compute Pass@1
python -m evalplus.evaluate \
    --dataset humaneval \
    --samples results/humaneval_claude.jsonl
```

### MBPP Evaluation

```bash
python evaluate/run_mbpp.py \
    --backend anthropic \
    --model claude-haiku-4-5-20251001 \
    --output results/mbpp_claude.jsonl

python -m evalplus.evaluate --dataset mbpp --samples results/mbpp_claude.jsonl
```

### Additional Metrics (Edit Distance + BLEU)

```bash
python evaluate/metrics.py \
    --samples results/humaneval_claude.jsonl \
    --dataset humaneval
```

### One-Shot Shell Scripts

```bash
# Run full HumanEval evaluation + scoring in one command
bash scripts/run_humaneval.sh anthropic claude-haiku-4-5-20251001

# GPT-3.5-turbo (paper results)
export OPENAI_API_KEY=sk-...
bash scripts/run_humaneval.sh openai gpt-3.5-turbo
```

---

## 🔬 Reproducing Paper Results

To reproduce the **exact** results from Table 2 (GPT-3.5-turbo):

```bash
export OPENAI_API_KEY=sk-...

# HumanEval → 86.6% Pass@1
python evaluate/run_humaneval.py \
    --backend openai --model gpt-3.5-turbo \
    --max-cot 3 --max-tests 5 --max-code 3 \
    --max-repair-rounds 3 --timeout 30 \
    --output results/humaneval_gpt35.jsonl

python -m evalplus.evaluate --dataset humaneval --samples results/humaneval_gpt35.jsonl

# MBPP → 79.2% Pass@1
python evaluate/run_mbpp.py \
    --backend openai --model gpt-3.5-turbo \
    --max-repair-rounds 3 \
    --output results/mbpp_gpt35.jsonl

python -m evalplus.evaluate --dataset mbpp --samples results/mbpp_gpt35.jsonl
```

> **Note:** Results may vary slightly due to LLM sampling randomness. The paper averages over 10 runs.

---

## ⚙️ Configuration

All hyperparameters are controlled via YAML configs or CLI flags:

| Parameter | Default | Description |
|---|:---:|---|
| `max_cot_prompts` | 3 | CoT prompt candidates per problem |
| `max_test_cases` | 5 | Test case candidates per problem |
| `max_code_snippets` | 3 | Code snippet candidates per problem |
| `max_repair_rounds` | **3** | Max repair iterations (paper optimal) |
| `code_timeout` | 30s | Subprocess execution timeout |
| `temperature_gen` | 0.8 | LLM temperature for generation |
| `temperature_prune` | 0.0 | LLM temperature for pruning (deterministic) |

**Available config presets:**

| File | Backend | Model | Use Case |
|---|---|---|---|
| `configs/claude.yaml` | Anthropic | claude-haiku-4-5 | Open-source, no OpenAI key |
| `configs/gpt35.yaml` | OpenAI | gpt-3.5-turbo | **Reproduce paper results** |
| `configs/gpt4.yaml` | OpenAI | gpt-4 | Best quality (94.5% HumanEval) |

---

## 🏗️ Project Structure

```
CodeCoR/
├── codecor/
│   ├── framework.py          # Main CodeCoR class (5-phase orchestrator)
│   ├── llm.py                # Unified LLM client (Anthropic + OpenAI)
│   ├── executor.py           # Safe sandboxed code execution
│   └── agents/
│       ├── prompt_agent.py   # Phase I: CoT generation + pruning
│       ├── test_agent.py     # Phase II: test case generation + pruning
│       ├── coding_agent.py   # Phase III/V: code generation + repair
│       └── repair_agent.py   # Phase V: repair advice + pruning
├── evaluate/
│   ├── run_humaneval.py      # HumanEval evaluation script
│   ├── run_mbpp.py           # MBPP evaluation script
│   └── metrics.py            # Edit distance + BLEU computation
├── configs/                  # YAML configuration presets
├── scripts/                  # One-liner evaluation scripts
├── examples/demo.py          # Interactive demo
└── tests/                    # Unit tests (pytest)
```

---

## 🧪 Testing

```bash
# Run all unit tests
python -m pytest tests/ -v

# Test a specific component
python -m pytest tests/test_framework.py::TestExecutor -v
```

---

## 📝 Citation

If you use CodeCoR in your research, please cite:

```bibtex
@article{pan2025codecor,
  title     = {CodeCoR: An LLM-Based Self-Reflective Multi-Agent Framework for Code Generation},
  author    = {Pan, Ruwei and Zhang, Hongyu and Liu, Chao},
  journal   = {arXiv preprint arXiv:2501.07811},
  year      = {2025},
  url       = {https://arxiv.org/abs/2501.07811}
}
```

---

## 📚 Related Work

| Method | Key Idea | HumanEval |
|---|---|:---:|
| [Self-Debugging](https://arxiv.org/abs/2304.05128) | LLM explains its own code | ~61% |
| [CodeChain](https://arxiv.org/abs/2310.08992) | Chain of self-revisions | ~63% |
| [CodeCoT](https://arxiv.org/abs/2308.08784) | CoT + self-examination | 79.3% |
| [MapCoder](https://arxiv.org/abs/2405.11403) | 4-agent sequential workflow | 80.5% |
| **CodeCoR (ours)** | **Self-reflective pruning + repair** | **86.6%** |

---

## 📄 License

This project is released under the [MIT License](LICENSE).

---

<div align="center">
<sub>Chongqing University · arXiv 2501.07811 · 2025</sub>
</div>
