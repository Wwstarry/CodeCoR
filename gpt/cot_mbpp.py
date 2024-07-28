import json
from human_eval.data import write_jsonl, read_problems
import openai
from openai import OpenAI
import re
import httpx

# client = openai.OpenAI(
#     base_url="https://api.xty.app/v1", 
#     api_key="",
#     http_client=httpx.Client(
#         base_url="https://api.xty.app/v1",
#         follow_redirects=True,
#     ),
# )

def write_jsonl(file_path, data):
 
    with open(file_path, 'a', encoding='utf-8') as f:
 
        for item in data:
            f.write(json.dumps(item) + '\n')

example = """
Input:
def factorial(n):
    \"\"\"
    Return the factorial of n.
    >>> factorial(2)
    2
    >>> factorial(0)
    1
    \"\"\"  

Output:
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

"""

def generate_one_completion(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    # print(chat_completion)
    return chat_completion.choices.pop().message.content

# print(generate_one_completion("hello"))
def remove_asserts(completion):
 
    completion_without_asserts = re.sub(r'assert\s+.*?(\n|\r\n?)', '', completion)
    return completion_without_asserts

problems = read_problems()

print("read_problems is done!")

def extract_code_if_present(text: str) -> str:
    match = re.search(r"```python\n([\s\S]*?)\n```", text)
    
 
    return match.group(1) if match else text
# print(problems)
samples = []
 
for task_id in list(problems)[60:530]:
    print(task_id)
 
    # prompt = problems[task_id]["text"] + '\nPlease cover all variables in the test case.' + ' '.join(problems[task_id]["test_list"]) + "Only provide the python code.Don't give examples and assertions."+sentence
    # prompt = problems[task_id]["text"] +'Here is the test list.\n'+' '.join(problems[task_id]["test_list"]) + "Only provide the code."

    prompt_cot = "Please provide the chain-of-thought of this problem step by step."+\
           "Here is the real problem.\n "+problems[task_id]["text"]+'\n'+' '.join(problems[task_id]["test_list"])
    
    cot = generate_one_completion(prompt_cot)

    prompt ="Given the problem description and chain-of-thought below, provide the Python code solution. "+\
           "No explanation or descriptive text is needed, just the code without examples.\n"+\
            problems[task_id]["text"]+'\n'+cot

    completion = generate_one_completion(prompt)
    real_code = extract_code_if_present(completion)
    # print(real_code)
 
    # completion_without_asserts = remove_asserts(completion)
    
    # print(completion_without_asserts)
     
    samples.append({"task_id": task_id, "completion":real_code})
 
    write_jsonl("samples_cot_mbpp_v1.jsonl", samples)
    samples = []

