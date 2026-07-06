"""
Test Agent — Phase II of CodeCoR.

Generates test cases guided by selected CoT prompts, then prunes
invalid ones using an LLM-based classifier (Figure 5 in the paper).

Paper §3.3 (Test Pruning):
  "After the Test Agent generates test cases, it uses another prompt to
   classify them. Empty input, incomplete format test cases, or invalid
   test cases are pruned."

Three discard categories:
  - Empty input        : no actual data provided
  - Incomplete format  : missing significant components for execution
  - Invalid test cases : wrong expected types or out-of-range values
"""
from __future__ import annotations

import re
import ast
import logging
from typing import List, Optional

from codecor.llm import LLMClient
from codecor.agents.base import BaseAgent

logger = logging.getLogger(__name__)

_GENERATION_SYSTEM = (
    "You are an expert software tester who writes precise Python assert statements "
    "to verify the correctness of functions."
)

# Uses ALL cot_prompts joined together so the full CoT pool guides generation
_GENERATION_TEMPLATE = """\
Given the programming task and the reasoning guides below, generate {n} diverse \
Python test cases as assert statements.

Task:
{task}

Reasoning guides (CoT):
{cot}

Requirements:
- Each test case must be a single assert statement: assert func_name(...) == expected
- Cover: typical inputs, boundary values, edge cases
- Use the exact function name from the task signature

Output ONLY the assert statements, one per line. No explanation, no comments.\
"""

# Paper Figure 5 — Test Pruning classifier prompt
_PRUNE_SYSTEM = (
    "You are a strict test case validator. "
    "Classify each assert statement as VALID or INVALID."
)

_PRUNE_TEMPLATE = """\
Classify each of the following Python assert statements for the given task.
Discard any that fall into these categories:
  - Empty input: the assert provides no meaningful test data
  - Incomplete format: the assert is missing required components for execution
  - Invalid test case: wrong expected type, nonsensical value, or wrong function name

Task:
{task}

Test cases to classify (one per line):
{test_cases}

For each test case, output exactly one line in this format:
  VALID: <original assert>
  INVALID: <original assert>

Output ONLY the classification lines, nothing else.\
"""


class TestAgent(BaseAgent):
    """
    Phase II: Test Case Generation with LLM-based validity pruning.

    generate() → list of raw assert-statement strings (uses ALL CoT prompts)
    prune()    → LLM classifies each as VALID/INVALID, removes invalid ones;
                 fallback to syntax-only check if LLM call fails
    """

    def __init__(self, llm: LLMClient, n: int = 5):
        super().__init__(llm)
        self.n = n

    def generate(
        self,
        task: str,
        cot_prompts: List[str],
        n: Optional[int] = None,
    ) -> List[str]:
        """
        Generate test cases using ALL selected CoT prompts.

        Paper: "In Phase-II, the selected CoT prompts direct the Test Agent
        in generating a pool of test cases."
        We concatenate all prompts to give the full CoT pool as context.
        """
        n = n or self.n
        # Use all CoT prompts, not just the first — paper uses the full CoT pool
        cot = "\n\n---\n\n".join(cot_prompts) if cot_prompts else task
        user_msg = _GENERATION_TEMPLATE.format(task=task, cot=cot, n=n)

        raw_tests: List[str] = []
        try:
            raw = self.llm.chat(
                [{"role": "user", "content": user_msg}],
                system=_GENERATION_SYSTEM,
                temperature=0.6,
            )
            for line in raw.splitlines():
                line = line.strip()
                if line.startswith("assert "):
                    raw_tests.append(line)
        except Exception as exc:
            logger.warning(f"TestAgent.generate failed: {exc}")

        return raw_tests

    def prune(self, test_cases: List[str], task: str = "") -> List[str]:
        """
        LLM-based test case pruning (paper §3.3, Test Pruning).

        Uses the LLM to classify each test case as VALID or INVALID.
        Falls back to syntax-only check if the LLM call fails.

        Paper categories for discard:
          - Empty input
          - Incomplete format
          - Invalid test cases (wrong types / out-of-range values)
        """
        if not test_cases:
            return []

        # --- Syntax pre-filter (fast, no API cost) ---
        syntactically_valid = []
        for tc in test_cases:
            tc = tc.strip()
            if not tc or not tc.startswith("assert "):
                continue
            try:
                ast.parse(tc)
                syntactically_valid.append(tc)
            except SyntaxError:
                logger.debug(f"TestAgent pruned (syntax): {tc!r}")

        if not syntactically_valid:
            logger.warning("TestAgent: no syntactically-valid test cases; keeping up to 3 raw")
            return test_cases[:3]

        # --- LLM-based semantic classification (paper Figure 5) ---
        if not task:
            # No task context → can only do syntax check
            return syntactically_valid

        tests_str = "\n".join(syntactically_valid)
        user_msg = _PRUNE_TEMPLATE.format(task=task, test_cases=tests_str)

        try:
            raw = self.llm.chat_prune(
                [{"role": "user", "content": user_msg}],
                system=_PRUNE_SYSTEM,
            )
            valid = self._parse_classifications(raw, syntactically_valid)
            if valid:
                logger.debug(f"TestAgent LLM pruned {len(syntactically_valid) - len(valid)} test cases")
                return valid
            # All classified as invalid → fallback to syntax-valid set
            logger.warning("TestAgent: LLM classified all as invalid; using syntax-valid fallback")
            return syntactically_valid

        except Exception as exc:
            logger.warning(f"TestAgent LLM prune failed ({exc}); using syntax-valid fallback")
            return syntactically_valid

    @staticmethod
    def _parse_classifications(raw: str, candidates: List[str]) -> List[str]:
        """
        Parse LLM classification output.
        Expected format per line: "VALID: assert ..." or "INVALID: assert ..."
        """
        valid = []
        for line in raw.splitlines():
            line = line.strip()
            if line.upper().startswith("VALID:"):
                assertion = line[len("VALID:"):].strip()
                # Accept if it matches one of the candidate assertions
                if assertion in candidates:
                    valid.append(assertion)
                elif any(c.startswith(assertion[:30]) for c in candidates if assertion):
                    # Fuzzy match in case the LLM reformats slightly
                    for c in candidates:
                        if c not in valid and assertion[:20] in c:
                            valid.append(c)
                            break
        return valid
