import json
from human_eval.data import write_jsonl, read_problems
import openai
from openai import OpenAI
import re
import httpx
import traceback
from typing import List, Tuple, Optional,Dict, Any


client = openai.OpenAI(
    base_url="https://api.xty.app/v1", 
    api_key=" ",
    http_client=httpx.Client(
        base_url="https://api.xty.app/v1",
        follow_redirects=True,
    ),
)


text = """Please return  Response according to Input only.Please follow this example:
### Input:
def factorial(n):
    \"\"\"
    Return the factorial of n.
    >>> factorial(2)
    2
    >>> factorial(0)
    1
    \"\"\"


### Response:
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


def generate_one_completion(prompt):
    prompt = prompt+"\n"+text
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo-0613",
    )

    # print(chat_completion)
    return chat_completion.choices.pop().message.content


problems = read_problems()

print("read_problems is done!")

samples = []

def write_jsonl(file_path, data):
 
    with open(file_path, 'a', encoding='utf-8') as f:
 
        for item in data:
            f.write(json.dumps(item) + '\n')


def extract_code_if_present(text: str) -> str:
    match = re.search(r"```python\n([\s\S]*?)\n```", text)
    return match.group(1) if match else text

for task_id in list(problems)[:]:  
    problem_info = problems[task_id]
    print(task_id)
    code = generate_one_completion(problem_info["prompt"])
    final_code = extract_code_if_present(code)
    samples.append({"task_id": task_id, "completion": final_code})
    write_jsonl("samples_few_shot.jsonl", samples)
    samples = []
 
