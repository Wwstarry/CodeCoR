"""
CodeCoR Framework — main orchestrator (optimized).

Implements the 5-phase self-reflective multi-agent pipeline from:
    "CodeCoR: An LLM-Based Self-Reflective Multi-Agent Framework for Code Generation"
    Pan et al., arXiv:2501.07811

Optimizations over baseline:
  - Docstring example extraction: `>>>` examples from problem prompt are added as
    guaranteed test cases (cannot be over-pruned by the LLM test classifier)
  - Self-verification: after repair rounds, best code is re-checked by LLM for
    systematic bugs (negative numbers, any/all, ceil vs int, etc.)
  - n_code=5: more candidate code snippets for better coverage
  - Anti-pattern warnings in generation and repair prompts
"""
from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

from codecor.llm import LLMClient
from codecor.executor import execute_code, count_passed
from codecor.agents.prompt_agent import PromptAgent
from codecor.agents.test_agent import TestAgent
from codecor.agents.coding_agent import CodingAgent
from codecor.agents.repair_agent import RepairAgent

logger = logging.getLogger(__name__)


@dataclass
class CodeCoRConfig:
    """Hyperparameters — optimized defaults for best HumanEval performance."""

    # Phase I
    max_cot_prompts: int = 3
    # Phase II
    max_test_cases: int = 5
    # Phase III — increased from paper's 3 to 5 for more diversity
    max_code_snippets: int = 5
    # Phase V — paper ablation (Figure 7): best at 3
    max_repair_rounds: int = 3
    # Execution
    code_timeout: int = 30
    # LLM temperatures
    temperature_gen: float = 0.8
    temperature_prune: float = 0.0
    # Optimizations
    use_self_verify: bool = True      # final LLM self-verification of best solution
    use_docstring_tests: bool = True  # always include >>> examples from problem prompt


# Internal representation of a ranked code entry.
# sort key: more passed tests first, fewer repair rounds first (paper §3.1)
@dataclass(order=True)
class RankedCode:
    neg_passed: int = field(compare=True)    # -passed so ascending = most passes first
    repair_rounds: int = field(compare=True) # ascending = fewer repairs first
    code: str = field(compare=False)
    passed: int = field(compare=False)


class CodeCoR:
    """
    End-to-end CodeCoR pipeline (Algorithm 1 in the paper).

    Usage
    -----
    llm = LLMClient(backend="openai", model="gpt-3.5-turbo")
    framework = CodeCoR(llm)
    solution = framework.generate(task_description, entry_point)
    """

    def __init__(self, llm: LLMClient, config: Optional[CodeCoRConfig] = None):
        self.config = config or CodeCoRConfig()
        self.llm = llm

        self.prompt_agent = PromptAgent(llm, n=self.config.max_cot_prompts)
        self.test_agent = TestAgent(llm, n=self.config.max_test_cases)
        self.coding_agent = CodingAgent(llm, n=self.config.max_code_snippets)
        self.repair_agent = RepairAgent(llm)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def generate(self, task_description: str, entry_point: str = "") -> str:
        """
        Run the full CodeCoR pipeline for a single programming task.

        Parameters
        ----------
        task_description : str
            Natural-language problem statement (HumanEval / MBPP prompt).
        entry_point : str
            Function name (optional, used in test generation).

        Returns
        -------
        str
            The highest-ranked code snippet.
        """
        cfg = self.config
        logger.info(f"CodeCoR.generate | task: {task_description[:80]}...")

        # ---- Phase I: Prompt Generation --------------------------------
        logger.info("Phase I: Prompt Generation")
        cot_pool = self.prompt_agent.generate(task_description, n=cfg.max_cot_prompts)
        cot_pool = self.prompt_agent.prune(cot_pool, task_description)
        logger.info(f"  CoT pool size after pruning: {len(cot_pool)}")

        # ---- Phase II: Test Case Generation ----------------------------
        logger.info("Phase II: Test Case Generation")

        # Optimization: extract docstring >>> examples as MANDATORY test cases.
        # These ground-truth examples bypass LLM pruning (they cannot be wrong)
        # and prevent the "self-reinforcing test bias" where generated tests
        # reflect the same misunderstanding as the generated code.
        docstring_tests: List[str] = []
        if cfg.use_docstring_tests:
            docstring_tests = self._extract_docstring_tests(task_description, entry_point)
            if docstring_tests:
                logger.info(f"  Extracted {len(docstring_tests)} docstring example tests")

        test_pool = self.test_agent.generate(
            task_description, cot_pool, n=cfg.max_test_cases
        )
        # LLM-based semantic pruning (paper §3.3 Test Pruning)
        test_pool = self.test_agent.prune(test_pool, task_description)

        # Merge: docstring tests first (highest priority), then LLM-generated tests
        # Deduplicate while preserving order
        seen = set(docstring_tests)
        merged = list(docstring_tests)
        for t in test_pool:
            if t not in seen:
                merged.append(t)
                seen.add(t)
        test_pool = merged
        logger.info(f"  Test pool size: {len(test_pool)} ({len(docstring_tests)} docstring + {len(test_pool)-len(docstring_tests)} LLM-generated)")

        # ---- Phase III: Code Generation --------------------------------
        logger.info("Phase III: Code Generation")
        code_pool = self.coding_agent.generate(
            task_description, cot_pool, n=cfg.max_code_snippets
        )
        # Code Pruning (paper §3.3): remove snippets with syntax errors
        code_pool = self.coding_agent.prune(code_pool)
        logger.info(f"  Code pool size after pruning: {len(code_pool)}")

        if not code_pool:
            logger.warning("CodeCoR: code pool is empty after pruning — returning empty string")
            return ""

        # ---- Phase IV: Result Checking ---------------------------------
        # Paper Algorithm 1 (lines 13–20):
        #   for code_snippet in code_snippet_pool:
        #     execution_result, error_messages = execute_code(...)
        #     if execution_result == "pass":
        #       ranked_code_set.append(code_snippet)
        #     elif requires_repair(error_messages):
        #       failed_code_snippets.append(code_snippet)
        #     else:
        #       ranked_code_set.append(code_snippet)
        #
        # Note on requires_repair on the INITIAL pass (first time code is run):
        #   The paper's stopping condition is "the failed test cases in the
        #   current round are similar to those in the previous round."
        #   On the very first pass there is no previous round, so
        #   requires_repair = True for all failures → all failed snippets enter
        #   the repair queue. The _is_stuck() check inside the repair loop
        #   handles the "no progress" condition across subsequent repair rounds.
        logger.info("Phase IV: Result Checking")
        ranked_set: List[RankedCode] = []
        # Each entry: (code, failed_assertions, error_details, repair_rounds)
        # failed_assertions = RAW assert strings that failed (paper: "failed test
        #   cases replace repair advice" when advice is pruned)
        pending: List[Tuple[str, List[str], List[str], int]] = []

        for code in code_pool:
            status, failed_assertions, error_details = execute_code(
                code, test_pool, timeout=cfg.code_timeout
            )
            if status == "pass":
                ranked_set.append(RankedCode(-len(test_pool), 0, code, len(test_pool)))
            else:
                # requires_repair = True for initial pass (no prior round)
                pending.append((code, failed_assertions, error_details, 0))

        logger.info(f"  {len(ranked_set)} passed, {len(pending)} queued for repair")

        # ---- Phase V: Code Repairing -----------------------------------
        # Paper Algorithm 1 (lines 22–32):
        #   while failed_code_snippets ≠ ∅:
        #     repair_suggestions = generate_repair_suggestions(failed_code_snippets)
        #     repair_suggestions = prune_repair_suggestions(repair_suggestions)
        #     revised_code_snippets = apply_repair_suggestions(repair_suggestions)
        #     for code_snippet in revised_code_snippets:
        #       execution_result, error_messages = execute_code(...)
        #       if pass: ranked_code_set.append(...)
        #       elif requires_repair: failed_code_snippets.append(...)
        #       [else: implicit, stuck code will not be re-queued]
        prev_failed: Dict[int, List[str]] = {}  # code identity → last failed assertions

        for repair_round in range(1, cfg.max_repair_rounds + 1):
            if not pending:
                break
            logger.info(f"Phase V round {repair_round}: {len(pending)} snippets")

            next_pending: List[Tuple[str, List[str], List[str], int]] = []

            for code, failed_assertions, error_details, rounds in pending:
                code_id = id(code)

                # Stopping condition: same failed assertions as previous round
                # → no progress → add to ranked set directly (requires_repair = False)
                if code_id in prev_failed and self._is_stuck(
                    failed_assertions, prev_failed[code_id]
                ):
                    passed = count_passed(code, test_pool, timeout=cfg.code_timeout)
                    ranked_set.append(RankedCode(-passed, rounds, code, passed))
                    logger.debug(f"  Stuck (no progress): added to ranked (passed={passed})")
                    continue

                prev_failed[code_id] = failed_assertions

                # Generate and prune repair advice
                # Paper §3.3 Repair Pruning fallback: "the failed test cases
                #   replace the repair advice" when advice is pruned.
                advice_list = self.repair_agent.generate(code, error_details)
                valid_advice, used_fallback = self.repair_agent.prune(
                    advice_list, code, task_description
                )

                if used_fallback or not valid_advice:
                    # Fallback: use the RAW failing assert statements as context
                    # (paper: "the failed test cases replace the repair advice")
                    advice = (
                        "The following test cases failed. Fix the code so they pass:\n"
                        + "\n".join(failed_assertions[:cfg.max_test_cases])
                    )
                else:
                    advice = valid_advice[0]

                # Re-generate code with repair advice (pass task for better context)
                repaired_list = self.coding_agent.repair(
                    code, error_details, advice, task=task_description
                )
                repaired_list = self.coding_agent.prune(repaired_list)

                for rep_code in repaired_list:
                    status, new_failed_assertions, new_error_details = execute_code(
                        rep_code, test_pool, timeout=cfg.code_timeout
                    )
                    if status == "pass":
                        ranked_set.append(
                            RankedCode(-len(test_pool), repair_round, rep_code, len(test_pool))
                        )
                    else:
                        # requires_repair: compare new failures to prior round
                        # (will be checked at the start of next iteration)
                        next_pending.append(
                            (rep_code, new_failed_assertions, new_error_details, repair_round)
                        )

            pending = next_pending

        # Any code still in pending after max_repair_rounds → add with pass count
        for code, failed_assertions, error_details, rounds in pending:
            passed = count_passed(code, test_pool, timeout=cfg.code_timeout)
            ranked_set.append(RankedCode(-passed, rounds, code, passed))

        # ---- Select and return highest-ranked code ---------------------
        ranked_set.sort()
        best = ranked_set[0]
        best_code = best.code

        # ---- Self-Verification (optimization) --------------------------
        # Ask the LLM to review the best solution for systematic bugs
        # (negative numbers, any/all, ceil vs int, etc.) that the repair loop
        # misses when generated tests reflect the same misunderstanding.
        if cfg.use_self_verify and best.passed < len(test_pool):
            logger.info("Self-verification: reviewing best solution for systematic bugs")
            verified_code = self.coding_agent.self_verify(best_code, task_description)
            if verified_code != best_code:
                # Re-run verified code against test pool to check if it's better
                v_status, v_failed, _ = execute_code(
                    verified_code, test_pool, timeout=cfg.code_timeout
                )
                v_passed = len(test_pool) - len(v_failed) if v_status == "fail" else len(test_pool)
                if v_passed >= best.passed:
                    logger.info(f"  Self-verify improved: {best.passed} → {v_passed} tests passed")
                    best_code = verified_code
                else:
                    logger.debug(f"  Self-verify did not improve ({v_passed} < {best.passed}), keeping original")

        logger.info(
            f"CodeCoR done. Best passed {best.passed}/{len(test_pool)} tests "
            f"(repair_rounds={best.repair_rounds})"
        )
        return best_code

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_docstring_tests(task: str, entry_point: str = "") -> List[str]:
        """
        Extract ground-truth test cases from the problem prompt's docstring
        >>> examples.

        These examples are guaranteed correct by the benchmark authors and
        cannot be over-pruned by the LLM test classifier. Including them
        prevents the "self-reinforcing test bias" where both generated code
        and generated tests reflect the same semantic misunderstanding.

        Example docstring fragment:
            >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
            False

        Extracted assert: assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False
        """
        tests: List[str] = []
        lines = task.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith(">>>"):
                call = line[3:].strip()  # e.g. "has_close_elements([1.0, 2.0], 0.5)"
                # Look for expected output on next non-empty line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines):
                    expected = lines[j].strip()
                    # Skip if expected is another >>> (chained call)
                    if not expected.startswith(">>>"):
                        # Build the assert
                        assert_stmt = f"assert {call} == {expected}"
                        # Basic validity check
                        try:
                            import ast as _ast
                            _ast.parse(assert_stmt)
                            tests.append(assert_stmt)
                        except SyntaxError:
                            # Some examples have complex output — try wrapping
                            pass
            i += 1

        return tests

    @staticmethod
    def _is_stuck(
        current_failed: List[str],
        prev_failed: Optional[List[str]],
    ) -> bool:
        """
        Return True if the set of failed test cases is identical to the
        previous round — indicating repair made no progress.

        Paper §3.1 Phase V: "code cannot be repaired when the failed test
        cases in the current round are similar to those in the previous round."
        """
        if prev_failed is None:
            return False
        return set(current_failed) == set(prev_failed)
