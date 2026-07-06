#!/bin/bash
# Reproduce CodeCoR MBPP results.
#
# Paper results (GPT-3.5-turbo):
#   MBPP:    79.2% Pass@1
#   MBPP-ET: 65.2% Pass@1

set -euo pipefail

BACKEND="${1:-anthropic}"
MODEL="${2:-claude-haiku-4-5-20251001}"
OUTDIR="results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SAMPLES="${OUTDIR}/mbpp_${BACKEND}_${MODEL}_${TIMESTAMP}.jsonl"

mkdir -p "${OUTDIR}"

echo "=============================================="
echo "CodeCoR — MBPP Evaluation"
echo "Backend : ${BACKEND}"
echo "Model   : ${MODEL}"
echo "Output  : ${SAMPLES}"
echo "=============================================="

python3 evaluate/run_mbpp.py \
    --backend "${BACKEND}" \
    --model "${MODEL}" \
    --dataset mbpp \
    --max-cot 3 \
    --max-tests 5 \
    --max-code 3 \
    --max-repair-rounds 3 \
    --timeout 30 \
    --output "${SAMPLES}"

echo ""
python3 -m evalplus.evaluate --dataset mbpp --samples "${SAMPLES}"
echo "Done. Samples: ${SAMPLES}"
