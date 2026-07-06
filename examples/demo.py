"""
Quick demo: run CodeCoR on a single HumanEval problem.

Usage
-----
# With OpenAI GPT-3.5-turbo (paper's model):
export OPENAI_API_KEY=sk-...
python examples/demo.py --backend openai --model gpt-3.5-turbo

# With Anthropic Claude via OpenAI-compatible proxy:
python examples/demo.py --backend openai \\
    --model aws.claude-opus-4.6 \\
    --api-key YOUR_KEY \\
    --base-url https://your-proxy.example.com/v1/openai/native

# With native Anthropic API:
export ANTHROPIC_API_KEY=sk-ant-...
python examples/demo.py --backend anthropic --model claude-haiku-4-5-20251001

# With a custom problem:
python examples/demo.py \\
    --backend openai --model gpt-3.5-turbo \\
    --problem "Write a Python function that returns the sum of all even numbers in a list."
"""
from __future__ import annotations

import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from codecor import CodeCoR, CodeCoRConfig, LLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# A representative HumanEval problem (HumanEval/0)
DEMO_PROBLEM = """\
from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    \"\"\"
"""


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default="anthropic", choices=["anthropic", "openai"])
    p.add_argument("--model", default="claude-haiku-4-5-20251001")
    p.add_argument("--api-key", default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--max-repair-rounds", type=int, default=3)
    p.add_argument("--problem", default=None, help="Custom problem description")
    return p.parse_args()


def main():
    args = parse_args()
    task = args.problem or DEMO_PROBLEM

    print("\n" + "=" * 60)
    print("CodeCoR Demo")
    print("=" * 60)
    print(f"Backend : {args.backend}")
    print(f"Model   : {args.model}")
    print(f"Task    :\n{task[:200]}{'...' if len(task) > 200 else ''}")
    print("=" * 60 + "\n")

    llm = LLMClient(
        backend=args.backend,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
    )
    config = CodeCoRConfig(max_repair_rounds=args.max_repair_rounds)
    framework = CodeCoR(llm, config)

    solution = framework.generate(task)

    print("\n" + "=" * 60)
    print("Generated Solution:")
    print("=" * 60)
    print(solution)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
