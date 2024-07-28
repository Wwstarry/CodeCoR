import time
import psutil
import json
from human_eval.data import write_jsonl, read_problems
import openai
from openai import OpenAI
import re
import httpx
from typing import List, Tuple, Optional, Dict, Any

# Record start metrics
start_time = time.time()
cpu_usage_start = psutil.cpu_percent(interval=1)
memory_usage_start = psutil.virtual_memory().used / (1024**3)  # GB
disk_io_start = psutil.disk_io_counters()
net_io_start = psutil.net_io_counters()

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
        model="gpt-3.5-turbo-0613",
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
        model="gpt-3.5-turbo-0613",
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

# Record end metrics
end_time = time.time()
duration = end_time - start_time  # Execution time
cpu_usage_end = psutil.cpu_percent(interval=1)
memory_usage_end = psutil.virtual_memory().used / (1024**3)  # GB
disk_io_end = psutil.disk_io_counters()
net_io_end = psutil.net_io_counters()

# Calculate I/O differences
read_bytes = (disk_io_end.read_bytes - disk_io_start.read_bytes) / (1024**2)  # MB
write_bytes = (disk_io_end.write_bytes - disk_io_start.write_bytes) / (1024**2)  # MB
sent_bytes = (net_io_end.bytes_sent - net_io_start.bytes_sent) / (1024**2)  # MB
recv_bytes = (net_io_end.bytes_recv - net_io_start.bytes_recv) / (1024**2)  # MB

# Memory usage increment
memory_used = memory_usage_end - memory_usage_start  # GB

def cost_analysis(duration, cpu_usage, memory_used, read_bytes, write_bytes, sent_bytes, recv_bytes):
    print(f"Total execution time: {duration:.2f} seconds")
    print(f"Average CPU usage: {cpu_usage}%")
    print(f"Memory usage increment: {memory_used:.2f} GB")
    print(f"Disk read: {read_bytes:.2f} MB, write: {write_bytes:.2f} MB")
    print(f"Network sent: {sent_bytes:.2f} MB, received: {recv_bytes:.2f} MB")

    # Add cost calculation logic as needed
    # e.g., converting resource usage to cost estimates

cost_analysis(duration, cpu_usage_end, memory_used, read_bytes, write_bytes, sent_bytes, recv_bytes)

# CodeCoR

# Total execution time: 123.69 seconds
# Average CPU usage: 0.8%
# Memory usage increment: 0.01 GB
# Disk read: 0.36 MB, write: 11.49 MB
# Network sent: 0.14 MB, received: 0.30 MB

# CodeCoT
# Total execution time: 156.38 seconds
# Average CPU usage: 0.8%
# Memory usage increment: -0.02 GB
# Disk read: 0.43 MB, write: 12.24 MB
# Network sent: 0.20 MB, received: 0.27 MB

# Total execution time: 142.88 seconds
# Average CPU usage: 0.4%
# Memory usage increment: 0.00 GB
# Disk read: 0.50 MB, write: 12.43 MB
# Network sent: 0.18 MB, received: 0.29 MB

# CoT
# Total execution time: 121.80 seconds
# Average CPU usage: 0.4%
# Memory usage increment: 0.01 GB
# Disk read: 1.25 MB, write: 16.21 MB
# Network sent: 0.16 MB, received: 0.22 MB

# SCoT
# Total execution time: 251.79 seconds
# Average CPU usage: 5.2%
# Memory usage increment: 0.21 GB
# Disk read: 55.32 MB, write: 162.90 MB
# Network sent: 0.72 MB, received: 1.15 MB

# Self-Planning
# Total execution time: 242.92 seconds
# Average CPU usage: 0.2%
# Memory usage increment: -0.02 GB
# Disk read: 1.02 MB, write: 31.16 MB
# Network sent: 0.35 MB, received: 0.74 MB
