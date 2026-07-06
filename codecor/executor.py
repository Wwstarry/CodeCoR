"""
Safe sandboxed code executor.

Runs generated Python code in an isolated subprocess with a timeout.
Supports two modes:
  - syntax_check(code)            → bool   (compile-only, no execution)
  - execute_code(code, tests, ..) → (status, failed_assertions, error_details)
"""
from __future__ import annotations

import os
import ast
import sys
import subprocess
import tempfile
import textwrap
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def syntax_check(code: str) -> bool:
    """Return True if code has no syntax errors."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def execute_code(
    code: str,
    test_cases: List[str],
    timeout: int = 30,
) -> Tuple[str, List[str], List[str]]:
    """
    Execute `code` against each test case in `test_cases`.

    Returns
    -------
    status : "pass" | "fail"
    failed_assertions : list of raw assert strings that failed
                        (paper §3.3 Repair Pruning fallback: "the failed test
                         cases replace the repair advice")
    error_details : list of "FAILED: <assert>\\n  <error_output>" strings
                    (used for logging and display)
    """
    if not syntax_check(code):
        err = "SyntaxError: code could not be parsed"
        return "fail", list(test_cases), [err]

    if not test_cases:
        status, out = _run_code(code, timeout)
        return ("pass" if status == 0 else "fail"), [], ([] if status == 0 else [out])

    failed_assertions: List[str] = []
    error_details: List[str] = []

    for tc in test_cases:
        full_code = _build_test_script(code, tc)
        status, output = _run_code(full_code, timeout)
        if status != 0:
            failed_assertions.append(tc.strip())
            error_details.append(f"FAILED: {tc.strip()}\n  {output.strip()}")

    if not failed_assertions:
        return "pass", [], []
    return "fail", failed_assertions, error_details


def count_passed(
    code: str,
    test_cases: List[str],
    timeout: int = 30,
) -> int:
    """Return the number of test cases passed (without short-circuiting)."""
    if not syntax_check(code) or not test_cases:
        return 0
    passed = 0
    for tc in test_cases:
        full_code = _build_test_script(code, tc)
        status, _ = _run_code(full_code, timeout)
        if status == 0:
            passed += 1
    return passed


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_test_script(code: str, test_case: str) -> str:
    """Combine user code with a single test-case assertion."""
    return textwrap.dedent(f"""
{code}

# --- auto-generated test ---
try:
    {test_case.strip()}
except AssertionError as _e:
    import sys
    print(f"AssertionError: {{_e}}", file=sys.stderr)
    sys.exit(1)
except Exception as _e:
    import sys
    print(f"{{type(_e).__name__}}: {{_e}}", file=sys.stderr)
    sys.exit(1)
""")


def _run_code(code: str, timeout: int) -> Tuple[int, str]:
    """
    Write code to a temp file and run it with `python3`.

    Returns (returncode, combined stderr+stdout).
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, f"TimeoutError: execution exceeded {timeout}s"
    except Exception as exc:
        return 1, f"{type(exc).__name__}: {exc}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
