import json
import torch
from transformers import AutoTokenizer, LlamaForCausalLM
from human_eval.data import  read_problems  # type: ignore
from tqdm import tqdm
from accelerate import Accelerator

# Initialize the Llama model and tokenizer
model_path = "Phind/Phind-CodeLlama-34B-v2"
model = LlamaForCausalLM.from_pretrained(model_path, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_path)


def generate_with_llama(prompt: str):
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)

    # Generate
    generate_ids = model.generate(inputs.input_ids.to("cuda"), max_new_tokens=384, do_sample=True, top_p=0.75, top_k=40, temperature=0.1)
    completion = tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    completion = completion.replace(prompt, "").split("\n\n\n")[0]

    return completion

def write_jsonl(file_path, data):
    
    with open(file_path, 'a', encoding='utf-8') as f:
 
        for item in data:
            f.write(json.dumps(item) + '\n')

def solve_problem_with_llama(prompt: str) -> str:

    solving_process_prompt = """
        Please understand the requirement and write a rough solving process. It starts with an input-output structure. 
        You should use three basic structures to build the solving process, including sequences, branches, and loops. 
        The necessary details should be written in natural languages.\n\n"""  + """\n\n
        Here are some examples:\n\n
        Question：\n
        def first_Repeated_Char(str):\n
        \"\"\"\n
        Write a Python function to find the first repeated character in a given string.\n
        \"\"\"\n
        Please understand the requirement and write a rough solving process. It starts with an input-output structure. 
        You should use three basic structures to build the solving process, including sequences, branches, and loops. 
        The necessary details should be written in natural languages.\n
        Answer:\n
        1. Initialize an empty set to store characters we've seen.
        2. Iterate through each character in the string.
        If the character is in our set, it's a repeat, and we return it.
        If it's not in the set, add it to the set and continue.
        3. If we finish the loop without finding a repeat, it means there are no repeated characters, so we can return an appropriate value like `None`.\n
    """+"Here is the real question:\n"+prompt

    solving_process = generate_with_llama(solving_process_prompt)
    print(solving_process)

    code_generation_prompt = solving_process + "\n\n" + "Based on the above solving process, Only return the code."
    generated_code = generate_with_llama(code_generation_prompt)
    print(generated_code)
    # return solving_process

    return generated_code

# Load HumanEval problems
problems = read_problems()
# print(problems)

# Process each problem
n=0
samples = []
for task_id in tqdm(problems):
    problem_info = problems[task_id]
    print(task_id)
    task_number = int(task_id.split('/')[1])
    if task_number < 480:
        continue
    prompt = problem_info['prompt']
    print(prompt)
    completion = solve_problem_with_llama(prompt)
    print(completion)
    samples.append({
        "task_id": task_id,
        "completion": completion
    })

    write_jsonl("cot_mbpp_samples.jsonl", samples)
    samples = []


