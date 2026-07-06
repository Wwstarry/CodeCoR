"""
Coding Agent — Phase III of CodeCoR.

Key improvements over baseline:
- n=5 code candidates for more diversity (was n=3)
- Anti-pattern warnings in generation prompt (negatives, any/all, ceil, sign×magnitude, etc.)
- Task description included in repair prompt for better context
- Self-verification step to catch systematic errors before submission
"""
from __future__ import annotations

import logging
from typing import List, Optional

from codecor.llm import LLMClient
from codecor.agents.base import BaseAgent
from codecor.executor import syntax_check

logger = logging.getLogger(__name__)

_GENERATION_SYSTEM = (
    "You are an expert Python programmer. "
    "Write clean, correct, and efficient Python functions. "
    "Pay meticulous attention to edge cases and the exact specification."
)

_GENERATION_TEMPLATE = """\
Implement the following Python function EXACTLY as specified.

Task description:
{task}

Reasoning guide (CoT):
{cot}

⚠️ CRITICAL — avoid these systematic mistakes:
• Negative numbers: include the sign when computing digit sums; NEVER use abs() to strip it
• Universal conditions: use all() not any() when EVERY element must satisfy a property
• Strict inequalities: if the spec says "greater than N", use > N, NOT >= N
• Return order: return the smallest value first unless explicitly told otherwise
• Ceiling division: use math.ceil(), NOT int() or // (which truncate toward zero)
• Per-element vs aggregate: process each row/group separately, NOT as a single merged pool
• Sign × magnitude: if result = sign × sum(abs(x)), compute BOTH; never return just the sign
• Two-digit check: include NEGATIVE two-digit numbers (e.g., -99 to -10 are two-digit)
• Position-based checks: check the specific required position (first, last, even-indexed)

Output ONLY the complete Python function definition (including the def line and any needed imports). \
No explanation, no markdown fences, no extra text.\
"""

_REPAIR_TEMPLATE = """\
The following Python code has errors. Fix it to correctly solve the task.

Original task:
{task}

Current code (WRONG):
```python
{code}
```

Failed test cases:
{failed_info}

Repair advice:
{advice}

⚠️ Double-check after fixing:
• Negative number sign handling
• any() vs all() — does EVERY element need to satisfy the condition?
• Strict > vs non-strict >= comparisons at boundaries
• math.ceil() vs int() for ceiling operations
• Per-row/per-element vs global aggregation

Output ONLY the corrected Python function. No explanation, no markdown fences.\
"""

_VERIFY_SYSTEM = (
    "You are a rigorous Python code reviewer and debugger. "
    "Identify bugs and return corrected code only."
)

_VERIFY_TEMPLATE = """\
Review this Python function against the specification and fix any bugs.

Specification:
{task}

Code to review:
```python
{code}
```

Specifically check for:
1. Negative number handling — is the sign preserved in digit computations?
2. any() vs all() — should EVERY element satisfy the condition, or just one?
3. Strict vs non-strict: "greater than N" means > N, not >= N
4. Return order — should the smaller value come first?
5. math.ceil() vs int() — is ceiling used where floor is not wanted?
6. Per-element vs global aggregation — are independent groups processed separately?
7. Missing position constraint — does a check apply only to certain indices?

If the code correctly implements the spec, output it UNCHANGED.
If there are bugs, output the CORRECTED version.

Output ONLY the Python function code. No explanation, no markdown.\
"""


class CodingAgent(BaseAgent):
    """
    Phase III: Code Generation with syntax pruning.
    Phase V  : Code Repair guided by RepairAgent advice.
    Bonus   : Self-verification step for catching systematic errors.
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
        """Generate `n` code snippet candidates (one per CoT, padded as needed)."""
        n = n or self.n
        snippets: List[str] = []

        # Build a list of CoTs to use — pad with repeats of the first if needed
        cots_to_use = list(cot_prompts[:n])
        cot_fallback = cot_prompts[0] if cot_prompts else task
        while len(cots_to_use) < n:
            cots_to_use.append(cot_fallback)

        for i, cot in enumerate(cots_to_use):
            user_msg = _GENERATION_TEMPLATE.format(task=task, cot=cot)
            try:
                raw = self.llm.chat(
                    [{"role": "user", "content": user_msg}],
                    system=_GENERATION_SYSTEM,
                )
                code = self._extract_code(raw)
                snippets.append(code)
            except Exception as exc:
                logger.warning(f"CodingAgent.generate attempt {i+1} failed: {exc}")

        return snippets if snippets else [task]

    def prune(self, snippets: List[str]) -> List[str]:
        """
        Code Pruning (paper §3.3): remove snippets with syntax errors.
        Falls back to keeping all if none pass syntax check.
        """
        valid = [s for s in snippets if syntax_check(s)]
        if not valid:
            logger.warning("CodingAgent: all snippets had syntax errors; keeping raw output")
            return snippets
        return valid

    def self_verify(self, code: str, task: str) -> str:
        """
        Self-verification: ask the LLM to review its solution for common bugs.

        This catches systematic errors (wrong sign handling, any/all confusion,
        ceil vs int, per-element vs aggregate) that the repair loop misses when
        generated test cases reflect the same misunderstanding as the wrong code.

        Returns a (potentially corrected) code string.
        """
        user_msg = _VERIFY_TEMPLATE.format(task=task, code=code)
        try:
            raw = self.llm.chat(
                [{"role": "user", "content": user_msg}],
                system=_VERIFY_SYSTEM,
                temperature=0.0,  # deterministic verification pass
            )
            verified = self._extract_code(raw)
            if syntax_check(verified):
                return verified
        except Exception as exc:
            logger.warning(f"CodingAgent.self_verify failed: {exc}")
        return code  # return original if verify fails

    def repair(
        self,
        original_code: str,
        failed_info: List[str],
        advice: str,
        task: str = "",
    ) -> List[str]:
        """Phase V: Generate repaired code based on Repair Agent's advice."""
        failed_str = "\n".join(failed_info[:10])
        user_msg = _REPAIR_TEMPLATE.format(
            task=task,
            code=original_code,
            failed_info=failed_str,
            advice=advice,
        )
        repaired: List[str] = []
        try:
            raw = self.llm.chat(
                [{"role": "user", "content": user_msg}],
                system=_GENERATION_SYSTEM,
            )
            repaired.append(self._extract_code(raw))
        except Exception as exc:
            logger.warning(f"CodingAgent.repair failed: {exc}")
            repaired.append(original_code)

        return repaired
