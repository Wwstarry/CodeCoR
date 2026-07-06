"""
BaseAgent — shared interface for all four CodeCoR agents.
"""
from __future__ import annotations

import re
import ast
import logging
from typing import List, Dict, Any, Optional

from codecor.llm import LLMClient

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    All agents share the LLM client and a common pruning evaluation helper.
    Subclasses implement `generate()` and `prune()`.
    """

    PRUNE_CRITERIA = ["clarity", "relevance", "conciseness", "context"]

    def __init__(self, llm: LLMClient):
        self.llm = llm

    # ------------------------------------------------------------------
    # Shared pruning-score helper (used by PromptAgent + RepairAgent)
    # ------------------------------------------------------------------

    def _eval_quality(
        self,
        item: str,
        task: str,
        context_label: str = "item",
    ) -> List[int]:
        """
        Ask the LLM to rate `item` against the four CodeCoR criteria.

        Returns a list of four 0/1 ints: [clarity, relevance, conciseness, context].
        Defaults to [0, 0, 0, 0] on parse failure.
        """
        prompt = (
            f"Evaluate the following {context_label} for the programming task.\n\n"
            f"Task:\n{task}\n\n"
            f"{context_label.capitalize()}:\n{item}\n\n"
            "Rate each criterion strictly as 1 (fully met) or 0 (not met):\n"
            "- Clarity: The item is clear and unambiguous\n"
            "- Relevance: The item is directly related to the task\n"
            "- Conciseness: The item is not overly complex or verbose\n"
            "- Context: The item provides enough contextual information\n\n"
            "Output ONLY a Python list like [1, 1, 1, 1] or [1, 0, 1, 1]. Nothing else."
        )
        raw = ""
        try:
            raw = self.llm.chat_prune([{"role": "user", "content": prompt}])
            # Extract first list-like expression from the response
            match = re.search(r"\[[\s\d,]+\]", raw)
            if match:
                scores = ast.literal_eval(match.group())
                if isinstance(scores, list) and len(scores) == 4:
                    return [int(bool(s)) for s in scores]
        except Exception as exc:
            logger.debug(f"Quality eval parse error: {exc}. Raw: {raw!r}")
        return [0, 0, 0, 0]

    # ------------------------------------------------------------------
    # Helper: extract code blocks from LLM output
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_code(text: str) -> str:
        """
        Robustly extract Python code from LLM output.

        Strategy:
        1. Extract from markdown code fence if present.
        2. Find the FIRST real `def` or `class` line at column 0 (no leading
           whitespace). Strip any prose preamble that appears before it —
           these cause IndentationError and silently crash the function.
        3. Prepend any valid `import`/`from X import Y` lines from the
           preamble (they may be needed by the function body).
        4. Return cleaned code.

        This handles the common LLM failure mode where prose from the problem
        description is output before the function definition, e.g.:
            "    from two integers, round it away from zero.\\n
             def closest_integer(value): ..."
        """
        # Step 1: Code fence extraction
        fence = re.search(r"```(?:python)?\n?(.*?)```", text, re.DOTALL)
        code = fence.group(1).strip() if fence else text.strip()

        lines = code.splitlines()

        # Step 2: Find the first top-level def/class line (column 0, not indented)
        def_idx = None
        for i, line in enumerate(lines):
            # Strictly at column 0 — no leading whitespace
            if re.match(r'^(def |class )\s*\w', line):
                def_idx = i
                break

        if def_idx is None or def_idx == 0:
            # No garbage preamble found — return as-is
            return code.strip()

        # Step 3: Collect valid import lines from the preamble to keep
        _VALID_IMPORT = re.compile(
            r'^(import\s+[A-Za-z_]\w*|from\s+[A-Za-z_]\w*(\.\w+)*\s+import\s+\S)'
        )
        import_lines = [
            lines[i] for i in range(def_idx)
            if _VALID_IMPORT.match(lines[i].strip()) and not lines[i][0:1].isspace()
        ]

        # Step 4: Assemble: imports + function definition
        kept = import_lines + lines[def_idx:]
        return "\n".join(kept).strip()
