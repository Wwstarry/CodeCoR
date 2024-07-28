import json
from human_eval.data import write_jsonl, read_problems
import openai
from openai import OpenAI
import re
import httpx

client = openai.OpenAI(
    base_url="https://api.xty.app/v1", 
    api_key="#add your key",
    http_client=httpx.Client(
        base_url="https://api.xty.app/v1",
        follow_redirects=True,
    ),
)

def write_jsonl(file_path, data):
    with open(file_path, 'a', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def generate_one_scot(prompt):
    prompt1 = "Please understand the requirement and write a rough solvingprocess,It starts with a input-output structure. Youshould use three basic structures to build the solvingprocess,includingsequences,branches,and loops.Thenecessary details should be written in natural languages.\n" + prompt + "\n" +\
            "Here are some examples:"+"\n"+"Question：\n"+\
             "def first_Repeated_Char(str):\n"+"\"\"\"\n"+"Write a Python function to find the first repeated \n"+\
             "character in a given string.\n"+"\"\"\"\n"+"Pass\n"+\
             "Please understand the requirement and write a rough solvingprocess,It starts with a input-output structure. Youshould use three basic structures to build the solvingprocess,includingsequences,branches,and loops.Thenecessary details should be written in natural languages.\n " + \
            "Answer:\nInput: str: a string\nOutput: ch: a repeated character in str\n"+\
            "1: for each character ch in str:\n2: if ch appears more than once in str:\n3: return ch\n4: return None\n"

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
    prompt2 = "please solve the problem:" + prompt + "\n" + first + "\n"

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

problems = read_problems()

print("read_problems is done!")

def extract_code_if_present(text: str) -> str:
    match = re.search(r"```python\n([\s\S]*?)\n```", text)
    
    return match.group(1) if match else text

samples = []
for task_id in list(problems)[356:530]:
    print(task_id)

    prompt_scot = generate_one_scot(problems[task_id]["text"])
    
    code = generate_one_competition(problems[task_id]["text"], prompt_scot)

    real_code = extract_code_if_present(code)
    
    samples.append({"task_id": task_id, "completion": real_code})
    write_jsonl("samples_scot_mbpp_v1.jsonl", samples)
    samples = []



