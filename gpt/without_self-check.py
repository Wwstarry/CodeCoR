import re
import time
import traceback
import openai
import signal
import statistics
import json
from human_eval.data import write_jsonl, read_problems
import httpx
from typing import List, Tuple, Optional


prompt_for_CodeCoT = """Please get Chain of Thought Reasoning, Code Implementation and Self-examination with Test Cases according to Task Description.
Here is the example:

### Task Description:
def factorial(n):
    \"\"\"
    Return the factorial of n.
    >>> factorial(2)
    2
    >>> factorial(0)
    1
    \"\"\"  

### Chain of Thought Reasoning:
1. **Understanding Factorial**: Recognize that the factorial of a number `n` is the product of all positive integers
from 1 to `n`.
2. **Choosing the Approach**: Decide between iterative and recursive approaches. Opt for the iterative approach to
avoid recursion limit issues for larger numbers.
3. **Implementing the Iterative Approach**: Start with initializing a result variable to 1. Then, multiply it sequentially
with every integer from 1 to `n`.
4. **Handling Edge Case**: Account for the edge case where `n` is 0. By definition, 0! (0 factorial) equals 1.
5. **Testing the Function**: After implementation, test the function with different values of `n` to ensure its
correctness.

### Code Implementation:
def factorial(n):
    \"\"\"
    Return the factorial of n.
    \"\"\"
    # Handle the edge case for 0 factorial
    if n == 0:
        return 1
    # Initialize the result variable
    result = 1
    # Iteratively compute the factorial
    for i in range(1, n + 1):
        result *= i
    return result

### Self-examination with Test Cases:

# Testing the function with various cases
assert factorial(0)==1 # factorial(0) should return 1
assert factorial(0)==1 # factorial(1) should return 1
assert factorial(2)==2 # factorial(2) should return 2
assert factorial(5)==120 # factorial(5) should return 120
assert factorial(10)==3628800 # factorial(10) should return 3628800


Below is the real Task Description.

### Task Description:

"""




def extract_code_and_tests(text: str):
    # Regex pattern for extracting code and test cases
    code_pattern = r"### Code Implementation:\n```python\n(.*?)```"
    test_pattern = r"### Self-examination with Test Cases:\n```python\n(.*?)```"
    # Extracting code implementation
    code_match = re.search(code_pattern, text, re.DOTALL)
    code = code_match.group(1).strip() if code_match else ""
    # Extracting test cases
    test_match = re.search(test_pattern, text, re.DOTALL)
    test_text = test_match.group(1).strip() if test_match else ""
    return code, test_text

client = openai.OpenAI(
 
    api_key="",
    http_client=httpx.Client(
        proxies="http://127.0.0.1:7890"
    )
)

def generate_first(prompt):
    prompt1 = prompt_for_CodeCoT+prompt

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt1,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices.pop().message.content

def generate_one_competition(prompt, first):
    prompt2 = first +"please solve the problem:" + prompt + "\n" + "Only return code.\n"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt2,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices.pop().message.content



def test_code(code: str, test_cases: str) -> List[str]:
    failed_tests = []
    namespace = {'List': List}  
    try:
  
        exec(code, namespace)
        for test_case in test_cases.split("\n"):
            if test_case.strip().startswith("assert"):
                try:
                    exec(test_case, namespace)
                except AssertionError as e:
 
                    failed_tests.append((test_case, str(e)))
                except Exception as e:
 
                    failed_tests.append((test_case, "Error: " + str(e)))
    except Exception as e:
 
        failed_tests.append(("Code Execution Error", "Error: " + traceback.format_exc()))

    failed_tests = [str(item) for item in failed_tests]
    
    return failed_tests

def generate_code_from_feedback(feedback):
 
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": feedback,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices.pop().message.content


 
def write_jsonl(file_path, data):
 
    with open(file_path, 'a', encoding='utf-8') as f:
 
        for item in data:
            f.write(json.dumps(item) + '\n')

 
problems = read_problems()
# print("read_problems is done!")

 
samples = []

for task_id in list(problems)[115:]:  
    problem_info = problems[task_id]
    print(task_id)
    
    first_step = generate_first(problem_info["prompt"])
    
    code, test_cases = extract_code_and_tests(first_step)

    test_cases+=problem_info["test"]


    feedback = code

    n=0

    prime_code=code

    while True:
 
        failed_tests = test_code(code, test_cases)

        if n>3:
            code=prime_code
            break

        if not failed_tests:
 
            break
    
 
        feedback += "\nFailed tests:\n" + "\n".join(failed_tests)
 
        prompt_feedback = code + '\n' + feedback + '\n' + 'You are a teacher, please follow the step-by-step analysis of error causes and give guidance to students based on error use cases and codes.'
        reply = generate_code_from_feedback(prompt_feedback)
        print(reply)
        prompt_cor = code + reply
        new_code = generate_code_from_feedback(prompt_cor)
        print(new_code)
        
 
        code = new_code
        print(code)

        n+=1
        

    samples.append({"task_id": task_id, "completion": code})
 
    write_jsonl("samples_pycor.jsonl", samples)
    samples = []


