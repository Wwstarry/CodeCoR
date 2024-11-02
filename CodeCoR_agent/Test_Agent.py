import json
from human_eval.data import read_problems
import openai
from openai import OpenAI
import httpx
import ell
import re
import traceback
from typing import List, Tuple, Optional,Dict, Any
import subprocess

Test_example = """
### Problem:
Write a function called factorial that computes the factorial of a given non-negative integer n, where the 
factorial of a number is the product of all positive integers up to that number.

### Test Cases:
assert factorial(0)==1 # factorial(0) should return 1
assert factorial(0)==1 # factorial(1) should return 1
assert factorial(2)==2 # factorial(2) should return 2
assert factorial(5)==120 # factorial(5) should return 120
assert factorial(10)==3628800 # factorial(10) should return 3628800
"""


@ell.simple(model="gpt-3.5-turbo-0613", client=client)
def Test_Agent(problem: str):
    """You are a Test Agent."""  # System prompt
    
    return (
        "Here is an example.\n" + Test_example + "Please generate three tests for the problem:\n"
        + f"{problem}\n"
        "Please only provide the tests."
    )


@ell.simple(model="gpt-3.5-turbo-0613", client=client)
def Test_Agent(test_case: str):
    """You are a Test Agent."""
    Test_template = """
    ### Empty Input: Return 1 if the input is not empty, otherwise return 0.
    ### Incomplete Format: Return 1 if matches expected format, otherwise return 0.
    ### Invalid Test Cases: Return 1 if no obvious invalid values, otherwise return 0.
    ### Output should follow the example: [1,1,1]
    """
    
    return Test_template + f"Evaluate this test case: {test_case}\nPlease only provide the list."