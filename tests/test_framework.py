"""
Unit tests for the CodeCoR framework.

Run with:
    python -m pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import MagicMock, patch

from codecor.executor import syntax_check, execute_code, count_passed
from codecor.agents.base import BaseAgent
from codecor.framework import CodeCoR, CodeCoRConfig
from codecor.llm import LLMClient


# ---------------------------------------------------------------------------
# Executor tests
# ---------------------------------------------------------------------------

class TestExecutor:
    def test_syntax_check_valid(self):
        assert syntax_check("def f(x):\n    return x + 1") is True

    def test_syntax_check_invalid(self):
        assert syntax_check("def f(x)\n    return x") is False

    def test_execute_pass(self):
        code = "def add(a, b):\n    return a + b"
        tests = ["assert add(1, 2) == 3", "assert add(-1, 1) == 0"]
        status, failed_assertions, error_details = execute_code(code, tests)
        assert status == "pass"
        assert failed_assertions == []
        assert error_details == []

    def test_execute_fail(self):
        code = "def add(a, b):\n    return a - b"  # wrong implementation
        tests = ["assert add(1, 2) == 3"]
        status, failed_assertions, error_details = execute_code(code, tests)
        assert status == "fail"
        assert "assert add(1, 2) == 3" in failed_assertions
        assert len(error_details) > 0

    def test_execute_fail_returns_raw_assertions(self):
        """Repair fallback uses raw assert strings, not formatted error messages."""
        code = "def add(a, b):\n    return a - b"
        tests = ["assert add(1, 2) == 3", "assert add(0, 0) == 0"]
        status, failed_assertions, _ = execute_code(code, tests)
        assert status == "fail"
        # failed_assertions should be the raw assert strings, not error messages
        assert all(a.startswith("assert ") for a in failed_assertions)

    def test_execute_timeout(self):
        code = "def f():\n    x = 1\n    x = 1\n    x = 1\n    x = 1\n    x = 1"
        tests = ["assert True"]
        status, _, _ = execute_code(code, tests, timeout=1)
        assert status in ("pass", "fail")

    def test_count_passed(self):
        code = "def add(a, b):\n    return a + b"
        tests = ["assert add(1, 2) == 3", "assert add(0, 0) == 0", "assert add(-1, 1) == 0"]
        n = count_passed(code, tests)
        assert n == 3

    def test_execute_no_tests(self):
        code = "x = 1 + 1"
        status, _, _ = execute_code(code, [])
        assert status == "pass"


# ---------------------------------------------------------------------------
# BaseAgent quality eval tests
# ---------------------------------------------------------------------------

class TestBaseAgent:
    def test_extract_code_plain(self):
        code = "def f(x):\n    return x"
        assert BaseAgent._extract_code(code) == code

    def test_extract_code_fenced(self):
        fenced = "```python\ndef f(x):\n    return x\n```"
        assert BaseAgent._extract_code(fenced) == "def f(x):\n    return x"

    def test_extract_code_no_lang_fence(self):
        fenced = "```\ndef f(x):\n    return x\n```"
        assert BaseAgent._extract_code(fenced) == "def f(x):\n    return x"


# ---------------------------------------------------------------------------
# Framework integration test (with mocked LLM)
# ---------------------------------------------------------------------------

class TestCodeCoRFramework:
    """
    Integration tests for the full CodeCoR pipeline.
    Agents are mocked directly to avoid prompt-content fragility.
    """

    CORRECT_CODE = (
        "def has_close_elements(numbers, threshold):\n"
        "    for i in range(len(numbers)):\n"
        "        for j in range(i+1, len(numbers)):\n"
        "            if abs(numbers[i] - numbers[j]) < threshold:\n"
        "                return True\n"
        "    return False"
    )

    WRONG_CODE = "def add(a, b):\n    return a - b"
    CORRECT_ADD = "def add(a, b):\n    return a + b"

    def _make_framework_with_mocked_agents(
        self,
        cot_pool=None,
        test_pool=None,
        code_pool=None,
        repair_code=None,
        config=None,
    ):
        """Build a CodeCoR instance with all 4 agents mocked at the agent level."""
        mock_llm = MagicMock(spec=LLMClient)
        cfg = config or CodeCoRConfig(
            max_cot_prompts=1,
            max_test_cases=2,
            max_code_snippets=1,
            max_repair_rounds=2,
        )
        framework = CodeCoR(mock_llm, cfg)

        # Mock PromptAgent
        framework.prompt_agent = MagicMock()
        framework.prompt_agent.generate.return_value = cot_pool or ["Step 1: Compare pairs. Step 2: Return True if close."]
        framework.prompt_agent.prune.return_value = cot_pool or ["Step 1: Compare pairs. Step 2: Return True if close."]

        # Mock TestAgent
        framework.test_agent = MagicMock()
        framework.test_agent.generate.return_value = test_pool or [
            "assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False",
            "assert has_close_elements([1.0, 2.8, 3.0], 0.3) == True",
        ]
        framework.test_agent.prune.return_value = test_pool or [
            "assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False",
            "assert has_close_elements([1.0, 2.8, 3.0], 0.3) == True",
        ]

        # Mock CodingAgent
        framework.coding_agent = MagicMock()
        framework.coding_agent.generate.return_value = code_pool or [self.CORRECT_CODE]
        framework.coding_agent.prune.return_value = code_pool or [self.CORRECT_CODE]
        framework.coding_agent.repair.return_value = [repair_code or self.CORRECT_CODE]

        # Mock RepairAgent
        framework.repair_agent = MagicMock()
        framework.repair_agent.generate.return_value = ["Fix the logic error."]
        framework.repair_agent.prune.return_value = (["Fix the logic error."], False)

        return framework

    def test_generate_returns_code(self):
        """Basic test: correct code is generated and returned."""
        framework = self._make_framework_with_mocked_agents()
        task = (
            "from typing import List\n\n"
            "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n"
            '    """Check if any two numbers are closer than threshold."""\n'
        )
        solution = framework.generate(task, "has_close_elements")
        assert "def " in solution
        assert isinstance(solution, str)
        assert len(solution) > 10

    def test_generate_all_tests_pass(self):
        """Code that passes all generated tests is returned directly (no repair)."""
        framework = self._make_framework_with_mocked_agents(
            code_pool=[self.CORRECT_CODE],
            test_pool=[
                "assert has_close_elements([1.0, 2.0, 3.0], 0.5) == False",
                "assert has_close_elements([1.0, 2.8, 3.0], 0.3) == True",
            ],
        )
        solution = framework.generate("def has_close_elements(numbers, threshold): pass", "has_close_elements")
        assert "has_close_elements" in solution
        # Repair agent should NOT have been called
        framework.repair_agent.generate.assert_not_called()

    def test_generate_with_repair(self):
        """Code that fails tests triggers the repair loop."""
        wrong_code = "def add(a, b):\n    return a - b"
        correct_code = "def add(a, b):\n    return a + b"

        framework = self._make_framework_with_mocked_agents(
            code_pool=[wrong_code],
            test_pool=["assert add(1, 2) == 3", "assert add(0, 0) == 0"],
            repair_code=correct_code,
            config=CodeCoRConfig(
                max_cot_prompts=1, max_test_cases=2,
                max_code_snippets=1, max_repair_rounds=3,
            ),
        )
        # Also make coding_agent.prune return the correct code for repaired snippet
        framework.coding_agent.prune.side_effect = lambda snippets: snippets

        solution = framework.generate("def add(a, b): pass", "add")
        assert "def " in solution
        # Repair agent should have been invoked
        framework.repair_agent.generate.assert_called()


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
