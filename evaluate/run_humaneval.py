"""
HumanEval / HumanEval+ evaluation script for CodeCoR.

Supports:
  - HumanEval (164 problems, original OpenAI benchmark)
  - HumanEval+ (EvalPlus extended test suites)

Usage
-----
python evaluate/run_humaneval.py \\
    --backend anthropic \\
    --model claude-haiku-4-5-20251001 \\
    --dataset humaneval \\
    --max-repair-rounds 3 \\
    --output results/humaneval_claude_haiku.jsonl

Then evaluate Pass@1:
    python -m evalplus.evaluate --dataset humaneval \\
        --samples results/humaneval_claude_haiku.jsonl
"""
from __future__ import annotations

import sys
import os
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Optional

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from codecor import CodeCoR, CodeCoRConfig, LLMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("evaluate.humaneval")


def parse_args():
    p = argparse.ArgumentParser(description="Run CodeCoR on HumanEval / HumanEval+")

    # LLM backend
    p.add_argument("--backend", default="anthropic", choices=["anthropic", "openai"],
                   help="LLM backend (default: anthropic)")
    p.add_argument("--model", default="claude-haiku-4-5-20251001",
                   help="Model name (default: claude-haiku-4-5-20251001)")
    p.add_argument("--api-key", default=None,
                   help="API key (falls back to env vars)")
    p.add_argument("--base-url", default=None,
                   help="Custom API base URL (overrides env vars)")

    # Dataset
    p.add_argument("--dataset", default="humaneval",
                   choices=["humaneval", "humaneval_plus"],
                   help="Dataset to evaluate on (default: humaneval)")

    # CodeCoR hyperparams
    p.add_argument("--max-cot", type=int, default=3,
                   help="Max CoT prompts per problem (default: 3)")
    p.add_argument("--max-tests", type=int, default=5,
                   help="Max test cases per problem (default: 5)")
    p.add_argument("--max-code", type=int, default=3,
                   help="Max code snippets per problem (default: 3)")
    p.add_argument("--max-repair-rounds", type=int, default=3,
                   help="Max repair rounds per snippet (default: 3, paper best)")
    p.add_argument("--timeout", type=int, default=30,
                   help="Code execution timeout in seconds (default: 30)")
    p.add_argument("--temperature", type=float, default=0.8,
                   help="Generation temperature (default: 0.8)")

    # I/O
    p.add_argument("--output", default="results/humaneval_samples.jsonl",
                   help="Output JSONL file for samples")
    p.add_argument("--start-idx", type=int, default=0,
                   help="Start from this problem index (for resuming)")
    p.add_argument("--end-idx", type=int, default=None,
                   help="Stop after this problem index")
    p.add_argument("--problem-id", default=None,
                   help="Run a single problem by task_id (e.g. HumanEval/0)")

    return p.parse_args()


def load_dataset(dataset_name: str):
    """Load HumanEval or HumanEval+ via evalplus."""
    if dataset_name == "humaneval":
        from evalplus.data import get_human_eval_plus
        # get_human_eval_plus returns the original HumanEval problems too
        # we use base=True to get the original 164 problems without extra tests
        problems = get_human_eval_plus()
    elif dataset_name == "humaneval_plus":
        from evalplus.data import get_human_eval_plus
        problems = get_human_eval_plus()
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")
    return problems


def build_task_description(problem: dict) -> str:
    """
    Construct the task description string from a HumanEval problem dict.
    Matches what the paper sends to the LLM.
    """
    return problem.get("prompt", "").strip()


def format_solution_for_evalplus(generated_code: str, problem: dict) -> str:
    """
    Format the generated code so evalplus can execute it correctly.

    evalplus evaluates `solution` by executing it directly, so all necessary
    imports (e.g. 'from typing import List') must be present. Our CodeCoR
    output is a complete function (with 'def' line), so we prepend any
    import lines from the original prompt.

    Strategy:
      solution = <import lines from prompt> + "\n\n" + <generated function>
    """
    prompt = problem.get("prompt", "")
    import_lines = [
        line for line in prompt.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    if import_lines:
        header = "\n".join(import_lines)
        return header + "\n\n" + generated_code.strip()
    return generated_code.strip()


def main():
    args = parse_args()

    # ------------------------------------------------------------------ Setup
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing samples to support resumption
    existing: dict = {}
    if output_path.exists():
        with open(output_path) as f:
            for line in f:
                try:
                    s = json.loads(line)
                    existing[s["task_id"]] = s
                except Exception:
                    pass
        logger.info(f"Loaded {len(existing)} existing samples from {output_path}")

    # ------------------------------------------------------------------ LLM
    llm = LLMClient(
        backend=args.backend,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature_gen=args.temperature,
    )

    # ------------------------------------------------------------------ CodeCoR
    config = CodeCoRConfig(
        max_cot_prompts=args.max_cot,
        max_test_cases=args.max_tests,
        max_code_snippets=args.max_code,
        max_repair_rounds=args.max_repair_rounds,
        code_timeout=args.timeout,
        temperature_gen=args.temperature,
    )
    framework = CodeCoR(llm, config)

    # ------------------------------------------------------------------ Dataset
    logger.info(f"Loading dataset: {args.dataset}")
    problems = load_dataset(args.dataset)
    task_ids = sorted(problems.keys())

    # Filter range
    if args.problem_id:
        task_ids = [t for t in task_ids if t == args.problem_id]
    else:
        task_ids = task_ids[args.start_idx : args.end_idx]

    logger.info(f"Evaluating {len(task_ids)} problems with CodeCoR ({args.backend}/{args.model})")

    # ------------------------------------------------------------------ Main loop
    results = []
    n_done = 0
    n_skip = 0

    with open(output_path, "a") as fout:
        for task_id in task_ids:
            problem = problems[task_id]
            entry_point = problem.get("entry_point", "")

            # Skip already-done
            if task_id in existing:
                n_skip += 1
                continue

            task_desc = build_task_description(problem)
            logger.info(f"[{n_done+1}/{len(task_ids)}] {task_id}: {entry_point}")

            t0 = time.time()
            try:
                solution = framework.generate(task_desc, entry_point)
            except Exception as exc:
                logger.error(f"  FAILED: {exc}")
                solution = f"# Error: {exc}\ndef {entry_point}(*args, **kwargs):\n    pass"

            elapsed = time.time() - t0

            # Format for evalplus: prepend import lines from prompt
            formatted = format_solution_for_evalplus(solution, problem)

            sample = {
                "task_id": task_id,
                "solution": formatted,
                "raw_solution": solution,      # original CodeCoR output
                "elapsed_sec": round(elapsed, 2),
            }
            fout.write(json.dumps(sample) + "\n")
            fout.flush()

            results.append(sample)
            n_done += 1

            logger.info(f"  Done in {elapsed:.1f}s")

    # ------------------------------------------------------------------ Summary
    logger.info("=" * 60)
    logger.info(f"Evaluation complete.")
    logger.info(f"  Problems evaluated : {n_done}")
    logger.info(f"  Problems skipped   : {n_skip}")
    logger.info(f"  Output file        : {output_path}")
    logger.info("")
    logger.info("To compute Pass@1, run:")
    logger.info(f"  python -m evalplus.evaluate --dataset humaneval --samples {output_path}")


if __name__ == "__main__":
    main()
