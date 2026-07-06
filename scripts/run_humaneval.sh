#!/bin/bash
# Reproduce CodeCoR HumanEval results.
#
# Paper results (GPT-3.5-turbo):
#   HumanEval:    86.6% Pass@1
#   HumanEval-ET: 80.5% Pass@1
#
# Usage:
#   # With Anthropic Claude (configured via env):
#   bash scripts/run_humaneval.sh anthropic claude-haiku-4-5-20251001
#
#   # With OpenAI GPT-3.5-turbo (paper's original):
#   export OPENAI_API_KEY=sk-...
#   bash scripts/run_humaneval.sh openai gpt-3.5-turbo

set -euo pipefail

BACKEND="${1:-anthropic}"
MODEL="${2:-claude-haiku-4-5-20251001}"
OUTDIR="results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAMPLES="${OUTDIR}/humaneval_${BACKEND}_${MODEL}_${TIMESTAMP}.jsonl"

mkdir -p "${OUTDIR}"

echo "=============================================="
echo "CodeCoR — HumanEval Evaluation"
echo "Backend : ${BACKEND}"
echo "Model   : ${MODEL}"
echo "Output  : ${SAMPLES}"
echo "=============================================="

# Step 1: Generate solutions
python3 evaluate/run_humaneval.py \
    --backend "${BACKEND}" \
    --model "${MODEL}" \
    --dataset humaneval \
    --max-cot 3 \
    --max-tests 5 \
    --max-code 3 \
    --max-repair-rounds 3 \
    --timeout 30 \
    --output "${SAMPLES}"

echo ""
echo "Generation complete. Computing Pass@1..."
echo ""

# Step 2: Evaluate Pass@1
python3 -m evalplus.evaluate \
    --dataset humaneval \
    --samples "${SAMPLES}"

echo ""
echo "=============================================="
echo "Evaluation complete!"
echo "Samples: ${SAMPLES}"
echo "=============================================="
