"""
Prompt Agent — Phase I of CodeCoR.

Generates Chain-of-Thought (CoT) prompts for a given task description,
then prunes low-quality prompts using the four-criterion quality check.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from codecor.llm import LLMClient
from codecor.agents.base import BaseAgent

logger = logging.getLogger(__name__)

# Faithful reproduction of Figure 3 generation prompt from the paper
_GENERATION_SYSTEM = (
    "You are an expert software engineer skilled in breaking down complex "
    "programming problems into clear, step-by-step reasoning guides."
)

_GENERATION_TEMPLATE = """\
Given the following programming task, generate a detailed Chain-of-Thought (CoT) \
prompt that will guide an LLM to write correct Python code.

Task description:
{task}

Your CoT prompt should include:
1. A step-by-step breakdown of the algorithm needed
2. Key requirements and edge cases that must be handled
3. Suggested data structures or approaches
4. Any pitfalls or tricky parts to watch out for

Output a single, self-contained CoT prompt (not code, just the reasoning guide).\
"""


class PromptAgent(BaseAgent):
    """
    Phase I: Prompt Generation with self-reflective pruning.

    generate() → n candidate CoT prompts
    prune()    → keep only prompts scoring [1,1,1,1] on the four criteria;
                 fall back to highest-sum candidate if none pass perfectly.
    """

    def __init__(self, llm: LLMClient, n: int = 3):
        super().__init__(llm)
        self.n = n

    def generate(self, task: str, n: Optional[int] = None) -> List[str]:
        """Generate `n` CoT prompt candidates for `task`."""
        n = n or self.n
        prompts: List[str] = []
        user_msg = _GENERATION_TEMPLATE.format(task=task)

        for i in range(n):
            try:
                raw = self.llm.chat(
                    [{"role": "user", "content": user_msg}],
                    system=_GENERATION_SYSTEM,
                )
                prompts.append(raw.strip())
            except Exception as exc:
                logger.warning(f"PromptAgent.generate attempt {i+1} failed: {exc}")

        return prompts if prompts else [task]  # fallback: use raw task description

    def prune(self, candidates: List[str], task: str) -> List[str]:
        """
        Evaluate each candidate on [clarity, relevance, conciseness, context].
        Keep those scoring [1,1,1,1].  If none qualify, return the best one.
        """
        if not candidates:
            return [task]

        scored = []
        for cot in candidates:
            scores = self._eval_quality(cot, task, context_label="CoT prompt")
            total = sum(scores)
            scored.append((cot, scores, total))
            logger.debug(f"PromptAgent scores {scores} for: {cot[:60]}...")

        perfect = [cot for cot, scores, _ in scored if all(s == 1 for s in scores)]
        if perfect:
            return perfect

        # Fallback: return candidate(s) with highest total score
        best_total = max(t for _, _, t in scored)
        return [cot for cot, _, t in scored if t == best_total]
