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

Prompt_example = """
### Problem:
Write a function called factorial that computes the factorial of a given non-negative integer n, where the factorial of a number 
is the product of all positive integers up to that number.

### Chain of thought:
First, we recognize that the factorial of a number is the product of all positive integers from 1 to that number.
There are two common approaches to calculating the factorial: iteratively and recursively.
For this task, we'll go with the iterative approach as it's straightforward and 
avoids potential issues with recursion limits for larger numbers.
The iterative approach involves initializing a variable to 1 and then multiplying 
it with every integer from 1 to n.
We also need to handle the edge case where n is 0, since 0! (0 factorial) is defined as 1.
Finally, we'll test the function to ensure it works correctly.
"""


@ell.simple(model="gpt-3.5-turbo-0613", client=client)
def Prompt_Agent(problem: str):
    """You are a Prompt Agent."""
    
    return (
        "Here is an example.\n"+ Prompt_example+ "Please write chain of thought for the problem:\n"+ f"{problem}\n"
        "Please only provide chain of thought."
    )


@ell.simple(model="gpt-3.5-turbo-0613", client=client)
def Prompt_Agent(prompt: str):
    """You are a Prompt Agent."""
    Prompt_template = """
    ### Clarity: Return 1 if there is no ambiguity, otherwise return 0.
    ### Relevance: Return 1 if directly related to the task, otherwise return 0.
    ### Conciseness: Return 1 if concise, otherwise return 0.
    ### Context: Return 1 if provides enough contextual information, otherwise return 0.
    ### Output should follow the example: [1,1,1,1]
    """
    
    return Prompt_template+f"Evaluate this CoT prompt: {prompt} \n.Please only provide the list."
