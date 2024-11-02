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


@ell.simple(model="gpt-3.5-turbo-0613", client=client)
def Repair_Agent(code: str, feedback: str):
    """You are a Repair Agent.""" 
    
    return (
        "Please write repair advice for the code:\n"
        + f"{code}\n"
        "Here is the feedback of compiler:\n"
        + f"{feedback}\n"
        "Please only provide the advice."
    )

@ell.simple(model="gpt-3.5-turbo-0613", client=client)
def Repair_Agent(advice: str):
    """You are a Repair Agent"""
    Repair_template = """
    ### Clarity: Return 1 if there is no ambiguity, otherwise return 0.
    ### Relevance: Return 1 if related to test cases, otherwise return 0.
    ### Conciseness: Return 1 if concise, otherwise return 0.
    ### Context: Return 1 if provides enough contextual information, otherwise return 0.
    ### Output should follow the example: [1,1,1,1]
    """
    
    return Repair_template + f"Evaluate this repair advice: {advice}\nPlease only provide the list."