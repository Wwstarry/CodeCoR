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
def Code_Agent(problem: str, cot: str):
    """You are a Code Agent.""" # System prompt
    return f"Please write code for the problem:\n {problem} \n .More information:\n{cot}\n.Please only provide the code." 
