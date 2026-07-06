"""
Additional evaluation metrics from the CodeCoR paper (Table 3):
  - Average Edit Distance  (Levenshtein distance between generated and reference code)
  - Average BLEU Score     (corpus BLEU between generated and reference code)

These supplement the primary Pass@1 metric computed by evalplus.

Usage
-----
python evaluate/metrics.py \\
    --samples results/humaneval_claude_haiku.jsonl \\
    --dataset humaneval
"""
from __future__ import annotations

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def compute_edit_distance(generated: str, reference: str) -> int:
    """Levenshtein edit distance between two strings (character-level)."""
    try:
        import editdistance  # type: ignore
        return editdistance.eval(generated, reference)
    except ImportError:
        # Fallback pure-Python implementation
        m, n = len(generated), len(reference)
        dp = list(range(n + 1))
        for i, ch_g in enumerate(generated, 1):
            prev, dp[0] = dp[0], i
            for j, ch_r in enumerate(reference, 1):
                prev, dp[j] = dp[j], prev if ch_g == ch_r else 1 + min(prev, dp[j], dp[j-1])
        return dp[n]


def compute_bleu(generated: str, reference: str) -> float:
    """Sentence-BLEU score using NLTK."""
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction  # type: ignore
        ref_tokens = reference.split()
        hyp_tokens = generated.split()
        if not hyp_tokens:
            return 0.0
        smoothie = SmoothingFunction().method4
        return sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smoothie)
    except Exception as exc:
        logger.warning(f"BLEU computation failed: {exc}")
        return 0.0


def evaluate_metrics(
    samples_path: str,
    dataset_name: str = "humaneval",
) -> Dict[str, float]:
    """
    Compute average Edit Distance and BLEU between generated samples and
    ground-truth reference solutions.

    Parameters
    ----------
    samples_path : path to the generated samples JSONL file
    dataset_name : "humaneval" or "mbpp"

    Returns
    -------
    dict with keys: avg_edit_distance, avg_bleu
    """
    # Load generated samples
    samples: Dict[str, str] = {}
    with open(samples_path) as f:
        for line in f:
            s = json.loads(line.strip())
            samples[s["task_id"]] = s["solution"]

    # Load reference solutions
    if dataset_name.startswith("humaneval"):
        from evalplus.data import get_human_eval_plus
        problems = get_human_eval_plus()
    elif dataset_name.startswith("mbpp"):
        from evalplus.data import get_mbpp_plus
        problems = get_mbpp_plus()
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    edit_distances: List[float] = []
    bleu_scores: List[float] = []

    for task_id, solution in samples.items():
        if task_id not in problems:
            continue
        reference = problems[task_id].get("canonical_solution", "")
        if not reference:
            continue

        ed = compute_edit_distance(solution, reference)
        bl = compute_bleu(solution, reference)
        edit_distances.append(ed)
        bleu_scores.append(bl)

    avg_ed = sum(edit_distances) / len(edit_distances) if edit_distances else 0.0
    avg_bleu = sum(bleu_scores) / len(bleu_scores) if bleu_scores else 0.0

    return {
        "num_problems": len(edit_distances),
        "avg_edit_distance": round(avg_ed, 2),
        "avg_bleu": round(avg_bleu, 4),
    }


def parse_args():
    p = argparse.ArgumentParser(description="Compute Edit Distance and BLEU for CodeCoR samples")
    p.add_argument("--samples", required=True, help="Path to samples JSONL")
    p.add_argument("--dataset", default="humaneval",
                   choices=["humaneval", "humaneval_plus", "mbpp", "mbpp_plus"])
    return p.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    results = evaluate_metrics(args.samples, args.dataset)
    print(f"\n{'='*40}")
    print(f"Dataset           : {args.dataset}")
    print(f"Problems evaluated: {results['num_problems']}")
    print(f"Avg Edit Distance : {results['avg_edit_distance']}")
    print(f"Avg BLEU Score    : {results['avg_bleu']}")
    print(f"{'='*40}\n")
