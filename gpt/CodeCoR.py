#In order to facilitate your reproduction, we have restructured the code structure.
# If you cannot implement the code of any module, please read the paper and write the code. 
# For example, we have not given the function for reading jsonl files here. When you encounter a problem, you can pay attention to the return results of the API.
# Sometimes you need to use regular expressions for matching and filtering .
# (the matching function has been given in the code, but other situations are not excluded.)

import json
import re
import httpx
import traceback
from typing import List, Tuple, Optional, Dict, Any
import openai
from openai import OpenAI
from human_eval.data import write_jsonl, read_problems
import time

    
class BaseAgent:
    def __init__(self, client: OpenAI):
        self.client = client

class InitializationAgent(BaseAgent):
    def initialize_openai_client(self, api_key: str, base_url: str = "https://api.xty.app/v1") -> OpenAI:

        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            http_client=httpx.Client(
                base_url=base_url,
                follow_redirects=True,
            ),
        )
        return client


class PromptAgent(BaseAgent):
    def generate_cot_prompt(self, task_description: str, prompt_type: str = "detailed") -> str:

        if prompt_type == "detailed":
            cot_prompt = (
                "Please understand the requirement and write a rough solving process. "
                "It starts with an input-output structure. You should use three basic structures "
                "to build the solving process, including sequences, branches, and loops. "
                "The necessary details should be written in natural languages.\n" + task_description + "\n" +
                "Here are some examples:\n" +
                "Question:\n" +
                "def first_Repeated_Char(str):\n" +
                "\"\"\"\n" +
                "Write a Python function to find the first repeated character in a given string.\n" +
                "\"\"\"\n" +
                "Pass\n" +
                "Please understand the requirement and write a rough solving process. It starts with an input-output structure. "
                "You should use three basic structures to build the solving process, including sequences, branches, and loops. "
                "The necessary details should be written in natural languages.\n" +
                "Answer:\nInput: str: a string\nOutput: ch: a repeated character in str\n" +
                "1: for each character ch in str:\n2: if ch appears more than once in str:\n3: return ch\n4: return None\n"
            )
        elif prompt_type == "example_based":
            cot_prompt = (
                'Please return Chain of Thought Reasoning according to Input only. '
                'Please follow this example:\n'
                '### Input:\n'
                'def factorial(n):\n'
                '    """\n'
                '    Return the factorial of n.\n'
                '    >>> factorial(2)\n'
                '    2\n'
                '    >>> factorial(0)\n'
                '    1\n'
                '    """\n'
                '\n'
                '### Chain of thought:\n'
                'First, we recognize that the factorial of a number is the product of all positive integers from 1 to that number.\n'
                'There are two common approaches to calculating the factorial: iteratively and recursively.\n'
                "For this task, we'll go with the iterative approach as it's straightforward and avoids potential issues with recursion limits for larger numbers.\n"
                'The iterative approach involves initializing a variable to 1 and then multiplying it with every integer from 1 to n.\n'
                'We also need to handle the edge case where n is 0, since 0! (0 factorial) is defined as 1.\n'
                "Finally, we'll test the function to ensure it works correctly.\n"
                '\n'
            )
        else:
            raise ValueError("Invalid prompt_type. Choose either 'detailed' or 'example_based'.")
        
        return cot_prompt

    def generate_initial_solution(self, cot_prompt: str) -> str:

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": cot_prompt,
                }
            ],
            model="gpt-3.5-turbo-0613",
        )

        return chat_completion.choices.pop().message.content


class CodeAgent(BaseAgent):
    def generate_code_from_prompt(self, cot_prompt: str) -> str:

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": cot_prompt,
                }
            ],
            model="gpt-3.5-turbo-0613",
        )

        return chat_completion.choices.pop().message.content

    def extract_code_from_response(self, response: str) -> str:

        match = re.search(r"```python\n([\s\S]*?)\n```", response)
        return match.group(1) if match else response

    def optimize_and_validate_code(self, code: str) -> bool:

        try:
 
            exec(code)
            return True
        except Exception as e:
            print(f"Code validation failed: {e}")
            return False

    def generate_optimized_code(self, cot_prompt: str) -> str:
        """
        Generates and optimizes code based on the CoT prompt.

        Args:
        - cot_prompt (str): The generated CoT prompt.

        Returns:
        - str: The optimized and validated code.
        """
        while True:
            initial_response = self.generate_code_from_prompt(cot_prompt)
            initial_code = self.extract_code_from_response(initial_response)
            
            if self.optimize_and_validate_code(initial_code):
                return initial_code
            else:
                print("Re-optimizing code...")


class TestAgent(BaseAgent):
    def generate_test_cases(self, code: str) -> str:
        """
        Generates test cases for the given code using OpenAI.

        Args:
        - code (str): The generated code for which test cases are to be created.

        Returns:
        - str: The generated test cases.
        """
        prompt = (
            "Please return Chain of Thought Reasoning, Response and Testing the Function according to Input only. "
            "Please follow this example:\n"
            "### Input:\n"
            "def factorial(n):\n"
            "\"\"\"\n"
            "Return the factorial of n.\n"
            ">>> factorial(2)\n"
            "2\n"
            ">>> factorial(0)\n"
            "1\n"
            "\"\"\"\n"
            "### Testing the Function:\n"
            "```python\n"
            "assert factorial(0)==1 # factorial(0) should return 1\n"
            "assert factorial(1)==1 # factorial(1) should return 1\n"
            "assert factorial(2)==2 # factorial(2) should return 2\n"
            "assert factorial(5)==120 # factorial(5) should return 120\n"
            "assert factorial(10)==3628800 # factorial(10) should return 3628800\n"
            "```\n"
            "### Input:\n"
            + code + "\n"
            "### Testing the Function:\n"
        )
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo-0613",
        )

        return chat_completion.choices.pop().message.content

    def extract_tests(self, text: str) -> str:

        test_pattern = r"### Testing the Function:\n```python\n(.*?)```"
        test_match = re.search(test_pattern, text, re.DOTALL)
        test_text = test_match.group(1).strip() if test_match else ""
        
        return test_text

    def execute_code_and_tests(self, code: str, tests: str) -> List[str]:

        failed_tests = []
        namespace = {}  
        try:
            exec(code, namespace)  
            for test_case in tests.split("\n"):
                if test_case.strip().startswith("assert"):
                    try:
                        exec(test_case, namespace)
                    except AssertionError as e:
                        failed_tests.append(f"Test Failed: {test_case}, AssertionError: {str(e)}")
                    except Exception as e:
                        failed_tests.append(f"Test Failed: {test_case}, Error: {str(e)}")
        except Exception as e:
            failed_tests.append(f"Code Execution Error, Error: {traceback.format_exc()}")
        
        return failed_tests

    def test_generated_code(self, code: str) -> Tuple[bool, str]:

        test_cases_response = self.generate_test_cases(code)
        test_cases = self.extract_tests(test_cases_response)

        failed_tests = self.execute_code_and_tests(code, test_cases)
        
        if failed_tests:
            return False, "\n".join(failed_tests)
        else:
            return True, "Code and tests executed successfully."


class RepairAgent(BaseAgent):
    def generate_repair_suggestions(self, code: str, error_message: str) -> str:

        prompt = (
            f"The following Python code contains errors:\n\n{code}\n\n"
            f"Error message:\n{error_message}\n\n"
            "Please provide a detailed explanation of the errors and suggest specific fixes."
        )
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo-0613",
        )

        return chat_completion.choices.pop().message.content

    def apply_repair_suggestions(self, code: str, repair_suggestions: str) -> str:

        repaired_code = code
        return repaired_code

    def repair_and_optimize_code(self, code: str, error_message: str) -> str:

        repair_suggestions = self.generate_repair_suggestions(code, error_message)
        repaired_code = self.apply_repair_suggestions(code, repair_suggestions)
        
        return repaired_code

    def test_and_repair_code(self, code: str) -> Tuple[bool, str]:
 
        success, message = TestAgent(self.client).test_generated_code(code)
        if success:
            return True, code
        else:
 
            repaired_code = self.repair_and_optimize_code(code, message)
            
            success, final_message = TestAgent(self.client).test_generated_code(repaired_code)
            if success:
                return True, repaired_code
            else:
                return False, final_message


class ControlModule:
    def __init__(self, client: OpenAI, task_description: str, max_iterations: int, timeout: int):
        self.client = client
        self.task_description = task_description
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.iteration = 0

    def monitor_iterations(self) -> bool:
 
        if self.iteration > self.max_iterations:
            return True
        return False

    def control_code_generation(self, code: str, test_cases: str) -> str:
 
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                print(f"Timeout reached for this task. Moving to next task.")
                return ""
            
            failed_tests = TestAgent(self.client).execute_code_and_tests(code, test_cases)
            if not failed_tests:
                return code

            feedback = code + "\nFailed tests:\n" + "\n".join(failed_tests)
            new_code_response = CodeAgent(self.client).generate_code_from_prompt(feedback)
            code = CodeAgent(self.client).extract_code_from_response(new_code_response)

            self.iteration += 1
            if self.monitor_iterations():
                print(f"Max iterations reached for this task. Moving to next task.")
                return ""


if __name__ == "__main__":
    api_key = "your_api_key_here"
    initialization_agent = InitializationAgent(None)
    openai_client = initialization_agent.initialize_openai_client(api_key)

    problems = read_problems()
    samples = []

    for task_id in list(problems)[:]:
        problem_info = problems[task_id]
        print(task_id)

        prompt_agent = PromptAgent(openai_client)
        code_agent = CodeAgent(openai_client)
        test_agent = TestAgent(openai_client)
        control_module = ControlModule(openai_client, problem_info["prompt"], max_iterations=5, timeout=300)

        cot_prompt = prompt_agent.generate_cot_prompt(problem_info["prompt"])
        code = code_agent.generate_optimized_code(cot_prompt)
        test_cases = test_agent.generate_test_cases(code)
        test_cases = test_agent.extract_tests(test_cases)

        final_code = control_module.control_code_generation(code, test_cases)
        if final_code:
            samples.append({"task_id": task_id, "completion": final_code})

            write_jsonl("samples_CodeCoR_gpt_4.jsonl", samples)
            samples = [] 
#Sometimes the generation may be interrupted due to network problems. In order to restart the generation from the interrupted point, we save the result in a jsonl file every time we get it.

