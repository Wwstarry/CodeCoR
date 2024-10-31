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
        model="gpt-4-1106-preview",
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
        model="gpt-4-1106-preview",
    )

    return chat_completion.choices.pop().message.content

problems = read_problems()
print("read_problems is done!")

def extract_code_if_present(text: str) -> str:
    match = re.search(r"```python\n([\s\S]*?)\n```", text)
    return match.group(1) if match else text

samples = []
for task_id in list(problems)[:10]:  # only iterating over the first 10 tasks
    problem_info = problems[task_id]
    print(task_id)
    prompt1 = problems[task_id]["prompt"]
    first_step = generate_one_scot(prompt1)
    completion = generate_one_competition(prompt1, first_step)
    code = extract_code_if_present(completion)
    print(code)

    samples.append({"task_id": task_id, "completion": code})
    write_jsonl("samples_scot_gpt_4.jsonl", samples)
    samples = []





# def generate_one_competition(prompt,first):
#     prompt2 = "please solve the problem:" + prompt + "\n"+first + \
#              "# Please check the above solving process and write a code based on it. Note that the solving process may contain errors. " + \
#              "Here are some examples："+"\n"+\
#              "def first_Repeated_Char(str):\n"+"\"\"\"\n"+"Write a python function to find the first repeated \n"+\
#              "haracter in a given string.\n"+"\"\"\"\n"+"Pass\n"+\
#              "\"\"\"\n" +"Input: str: a string\nOutput: ch: a repeated character in str\n1: for each character ch in str:\n2: if ch appears more than once in str:\n3: return ch\n4: return None"+\
#              "\"\"\"\n"+"# Please check the above solving process and write a code based on it. Note that the solving process may contain errors."+\
#              "h = {}\nfor ch in str:\nif ch in h: \nreturn ch;\nelse: \nh[ch] = 0\nreturn None"


#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt2,
#             }
#         ],
#         model="gpt-3.5-turbo",
#     )

#     # print(chat_completion)
#     return chat_completion.choices.pop().message.content