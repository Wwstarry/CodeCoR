"""
MBPP / MBPP+ evaluation script for CodeCoR.

Usage
-----
python evaluate/run_mbpp.py \\
    --backend anthropic \\
    --model claude-haiku-4-5-20251001 \\
    --output results/mbpp_claude_haiku.jsonl

Then evaluate:
    python -m evalplus.evaluate --dataset mbpp \\
        --samples results/mbpp_claude_haiku.jsonl
"""
from __future__ import annotations

import sys
import json
import time
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from codecor import CodeCoR, CodeCoRConfig, LLMClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("evaluate.mbpp")


def parse_args():
    p = argparse.ArgumentParser(description="Run CodeCoR on MBPP / MBPP+")
    p.add_argument("--backend", default="anthropic", choices=["anthropic", "openai"])
    p.add_argument("--model", default="claude-haiku-4-5-20251001")
    p.add_argument("--api-key", default=None)
    p.add_argument("--base-url", default=None)
    p.add_argument("--dataset", default="mbpp", choices=["mbpp", "mbpp_plus"])
    p.add_argument("--max-cot", type=int, default=3)
    p.add_argument("--max-tests", type=int, default=5)
    p.add_argument("--max-code", type=int, default=3)
    p.add_argument("--max-repair-rounds", type=int, default=3)
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--output", default="results/mbpp_samples.jsonl")
    p.add_argument("--start-idx", type=int, default=0)
    p.add_argument("--end-idx", type=int, default=None)
    return p.parse_args()


def main():
    args = parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict = {}
    if output_path.exists():
        with open(output_path) as f:
            for line in f:
                try:
                    s = json.loads(line)
                    existing[s["task_id"]] = s
                except Exception:
                    pass
        logger.info(f"Loaded {len(existing)} existing samples")

    llm = LLMClient(
        backend=args.backend,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature_gen=args.temperature,
    )
    config = CodeCoRConfig(
        max_cot_prompts=args.max_cot,
        max_test_cases=args.max_tests,
        max_code_snippets=args.max_code,
        max_repair_rounds=args.max_repair_rounds,
        code_timeout=args.timeout,
        temperature_gen=args.temperature,
    )
    framework = CodeCoR(llm, config)

    # Load MBPP via evalplus
    from evalplus.data import get_mbpp_plus
    problems = get_mbpp_plus()
    task_ids = sorted(problems.keys())[args.start_idx : args.end_idx]
    logger.info(f"Evaluating {len(task_ids)} MBPP problems")

    n_done = 0
    with open(output_path, "a") as fout:
        for task_id in task_ids:
            if task_id in existing:
                continue
            problem = problems[task_id]
            task_desc = problem.get("prompt", "").strip()
            entry_point = problem.get("entry_point", "")

            logger.info(f"[{n_done+1}/{len(task_ids)}] {task_id}")
            t0 = time.time()
            try:
                solution = framework.generate(task_desc, entry_point)
            except Exception as exc:
                logger.error(f"  FAILED: {exc}")
                solution = f"# Error: {exc}\ndef {entry_point}(*args):\n    pass"

            elapsed = time.time() - t0
            # Prepend any imports from prompt
            prompt = problem.get("prompt", "")
            import_lines = [l for l in prompt.splitlines()
                            if l.strip().startswith(("import ", "from "))]
            formatted = ("\n".join(import_lines) + "\n\n" + solution.strip()
                         if import_lines else solution.strip())
            sample = {
                "task_id": task_id,
                "solution": formatted,
                "raw_solution": solution,
                "elapsed_sec": round(elapsed, 2),
            }
            fout.write(json.dumps(sample) + "\n")
            fout.flush()
            n_done += 1
            logger.info(f"  Done in {elapsed:.1f}s")

    logger.info(f"Done. Output: {output_path}")
    logger.info(f"To score: python -m evalplus.evaluate --dataset mbpp --samples {output_path}")


if __name__ == "__main__":
    main()
