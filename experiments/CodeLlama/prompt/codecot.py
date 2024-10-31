import traceback
from typing import List
import torch
from transformers import AutoTokenizer, LlamaForCausalLM
from human_eval.data import read_problems  # type: ignore
from tqdm import tqdm
from accelerate import Accelerator
import re
import json

# Initialize the Llama model and tokenizer
model_path = "Phind/Phind-CodeLlama-34B-v2"
model = LlamaForCausalLM.from_pretrained(model_path, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_path)


def write_jsonl(file_path, data):
 
    with open(file_path, 'a', encoding='utf-8') as f:

        for item in data:
            f.write(json.dumps(item) + '\n')

def generate_with_llama(prompt: str):
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

def generate_with_llama_step2(prompt: str):
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

agent1 = "You are a code developer assistant. Return the function code only."
# agent2 = "Please complete the code based on the given function description. Return the function code only."

text = """Please return Chain of Thought Reasoning, Response and Testing the Function according to Input only.Please follow this example:
### Input:
def factorial(n):
    \"\"\"
    Return the factorial of n.
    >>> factorial(2)
    2
    >>> factorial(0)
    1
    \"\"\"

###Chain of thought:
First, we recognize that the factorial of a number is the product of all positive integers from 1 to that number.
There are two common approaches to calculating the factorial: iteratively and recursively.
For this task, we'll go with the iterative approach as it's straightforward and avoids potential issues with recursion limits for larger numbers.
The iterative approach involves initializing a variable to 1 and then multiplying it with every integer from 1 to n.
We also need to handle the edge case where n is 0, since 0! (0 factorial) is defined as 1.
Finally, we'll test the function to ensure it works correctly.

### Testing the Function:
```python
assert factorial(0)==1 # factorial(0) should return 1
assert factorial(0)==1 # factorial(1) should return 1
assert factorial(2)==2 # factorial(2) should return 2
assert factorial(5)==120 # factorial(5) should return 120
assert factorial(10)==3628800 # factorial(10) should return 3628800
```

### Code:
```python
def factorial(n):
    \"\"\"
    >>> factorial(9)
    362880
    >>> factorial(0)
    1
    \"\"\"
    if n == 0:
        return 1
    result = 1
    for i in range(1, n+1):
        result *= i
    return result
```
"""
prompt1 = text+"Here is the real input.Please return Chain of Thought Reasoning only."
prompt2 = text+"Here is the real input.Please return the Test according to Input only."
prompt3 = text+"Here is the real input.Please return code according to Input only."

def generate_with_llama_step1(prompt: str):
    prompt=text+"Here is the real input.Please return Chain of Thought Reasoning, Response and Testing the Function according to Input only."+ prompt
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

def generate_with_llama_cot(prompt: str):
    prompt=text+"Here is the real input.Please return Chain of Thought Reasoning only."+ prompt
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

def generate_with_llama_test(prompt: str):
    prompt=text+"Here is the real input.Please return the Test according to Input only."+ prompt
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

def generate_with_llama_code(prompt: str):
    prompt=text+"Here is the real input.Please return code according to Input only."+ prompt
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

# def extract_code_and_tests(text: str):
#     # Regex pattern for extracting code and test cases
#     code_pattern = r"### Response:\n```python\n(.*?)```"
#     test_pattern = r"### Testing the Function:\n```python\n(.*?)```"
#     # Extracting code implementation
#     code_match = re.search(code_pattern, text, re.DOTALL)
#     code = code_match.group(1).strip() if code_match else ""
#     # Extracting test cases
#     test_match = re.search(test_pattern, text, re.DOTALL)
#     test_text = test_match.group(1).strip() if test_match else ""
#     return code, test_text

# def test_code(code: str, test_cases: str) -> List[str]:
#     failed_tests = []
#     namespace = {'List': List} 
#     try:
#         exec(code, namespace)  
#         for test_case in test_cases.split("\n"):
#             if test_case.strip().startswith("assert"):
#                 try:
#                     exec(test_case, namespace)
#                 except AssertionError as e:
#                     failed_tests.append(f"Test Failed: {test_case}, AssertionError: {str(e)}")
#                 except Exception as e:
#                     failed_tests.append(f"Test Failed: {test_case}, Error: {str(e)}")
#     except Exception as e:
#         failed_tests.append(f"Code Execution Error, Error: {traceback.format_exc()}")

#     return failed_tests

# def extract_code_if_present(text: str) -> str:
#     match = re.search(r"```python\n([\s\S]*?)\n```", text)
    

#     return match.group(1) if match else text

problems = read_problems()
# print(problems)
# Process each problem
samples = []
for task_id in tqdm(problems):
    problem_info = problems[task_id]
    print(task_id)
    task_number = int(task_id.split('/')[1])
    if task_number < 252:
        continue
    prompt = prompt1 + '\n' + problem_info["prompt"]
    cot = generate_with_llama(prompt)
    prompt = prompt3 + '\n' + problem_info["prompt"]
    code = generate_with_llama(prompt)
    prompt = prompt2 + '\n' + problem_info["prompt"]
    test = generate_with_llama(prompt)
    # cot = generate_with_llama_step1(problem_info["prompt"])
    # code, test_cases = extract_code_and_tests(cot)
    # feedback = code

    # n=0

    # while True:
 
    #     failed_tests = test_code(code, test_cases)

    #     if n>3:
    #         break

    #     if not failed_tests:
    #   
    #         break
    
    #  
    #     feedback += "\nFailed tests:\n" + "\n".join(failed_tests)
    #     # print(feedback)

    #     prompt_feedback = code + '\n' + feedback + '\n' + agent1
    #     new_code = generate_with_llama_step2(prompt_feedback)

    #     code = new_code
    #     # print(code)
    #     n+=1
    #     print(n)
    # final_code = extract_code_if_present(code)
    # print(final_code)
    print(cot)
    samples.append({
        "task_id": task_id,
        "cot": cot,
        "test":test,
        "code":code
    })
    write_jsonl("codecot_cot_mbpp_samples.jsonl", samples)
    samples = []