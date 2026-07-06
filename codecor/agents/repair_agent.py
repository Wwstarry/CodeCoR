"""
Repair Agent — Phase V of CodeCoR.

Analyzes failed code snippets, generates targeted repair advice,
and prunes low-quality advice using the four-criterion quality check.
If advice is pruned, the failed test cases are passed directly to the
Coding Agent as context (paper §3.3, Repair Pruning fallback).
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple

from codecor.llm import LLMClient
from codecor.agents.base import BaseAgent

logger = logging.getLogger(__name__)

_GENERATION_SYSTEM = (
    "You are an expert Python debugger. "
    "Analyze buggy code and provide precise, actionable repair advice."
)

_GENERATION_TEMPLATE = """\
The following Python code failed some test cases. Analyze the errors and provide \
specific repair advice.

Code:
```python
{code}
```

Failed test cases and errors:
{failed_info}

Provide targeted repair advice:
1. Identify exactly what is wrong (logical error, edge case missed, wrong algorithm, etc.)
2. Explain specifically how to fix it
3. Point to the problematic line(s) if possible

Be concise and actionable. Do NOT rewrite the code — provide advice only.\
"""

_PRUNE_TEMPLATE = """\
Evaluate the following repair advice for a programming task.

Code being repaired:
```python
{code}
```

Repair advice:
{advice}

Rate each criterion strictly as 1 (fully met) or 0 (not met):
- Clarity: The advice is clear and unambiguous
- Relevance: The advice directly addresses the actual code errors
- Conciseness: The advice is not overly verbose or off-topic
- Context: The advice provides enough context to guide the fix

Output ONLY a Python list like [1, 1, 1, 1]. Nothing else.\
"""


class RepairAgent(BaseAgent):
    """
    Phase V: Repair Advice Generation with quality pruning.

    generate() → repair advice string
    prune()    → validate advice; if pruned, return fallback (failed tests as context)
    """

    def __init__(self, llm: LLMClient):
        super().__init__(llm)

    def generate(
        self,
        code: str,
        failed_info: List[str],
    ) -> List[str]:
        """Generate one piece of targeted repair advice."""
        failed_str = "\n".join(failed_info[:10])
        user_msg = _GENERATION_TEMPLATE.format(code=code, failed_info=failed_str)

        advice_list: List[str] = []
        try:
            raw = self.llm.chat(
                [{"role": "user", "content": user_msg}],
                system=_GENERATION_SYSTEM,
            )
            advice_list.append(raw.strip())
        except Exception as exc:
            logger.warning(f"RepairAgent.generate failed: {exc}")

        return advice_list

    def prune(
        self,
        advice_list: List[str],
        code: str,
        task: str = "",
    ) -> Tuple[List[str], bool]:
        """
        Prune low-quality repair advice.

        Returns
        -------
        valid_advice : list of advice strings that passed quality check
        used_fallback : True if advice was pruned (caller should use failed tests directly)
        """
        if not advice_list:
            return [], True

        valid = []
        for advice in advice_list:
            # Custom pruning prompt for repair (uses code context, not task)
            prompt = _PRUNE_TEMPLATE.format(code=code, advice=advice)
            try:
                import re, ast
                raw = self.llm.chat_prune([{"role": "user", "content": prompt}])
                match = re.search(r"\[[\s\d,]+\]", raw)
                if match:
                    scores = ast.literal_eval(match.group())
                    if isinstance(scores, list) and len(scores) == 4:
                        if all(int(bool(s)) == 1 for s in scores):
                            valid.append(advice)
                            continue
            except Exception as exc:
                logger.debug(f"RepairAgent.prune eval error: {exc}")

            logger.debug(f"RepairAgent pruned advice: {advice[:80]}...")

        if valid:
            return valid, False

        # All advice pruned — caller falls back to using failed test cases directly
        logger.debug("RepairAgent: all advice pruned; using fallback (failed tests as context)")
        return [], True
