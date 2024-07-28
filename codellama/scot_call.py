import torch
from transformers import AutoTokenizer, LlamaForCausalLM
from human_eval.data import write_jsonl, read_problems  # type: ignore
from tqdm import tqdm
from accelerate import Accelerator
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

def solve_problem_with_llama(prompt: str) -> str:
    """
    Solves a coding problem by generating a rough solving process followed by code using the Llama model.
    """
    solving_process_prompt = """
        Please understand the requirement and write a rough solving plan. It starts with an input-output structure. 
        You should use three basic structures to build the solving process, including sequences, branches, and loops. 
        The necessary details should be written in natural languages.\n\n"""+ """\n\n
        Here are some examples:\n\n
        Question：\n
        prime_fib returns n-th number that is a Fibonacci number and it's also prime.
        Answer:\n
        Input: str: a string\n
        Output: ch: a repeated character in str\n
        1: for each character ch in str:\n
        2: if ch appears more than once in str:\n
        3: return ch\n
        4: return None\n
    """ +"Here is the real question.\n"+ prompt 

    solving_process = generate_with_llama(solving_process_prompt)

    code_generation_prompt = solving_process + "\n\n" + "Based on the above solving process, please write the code."
    generated_code = generate_with_llama(code_generation_prompt)

    return generated_code

# Load HumanEval problems
problems = read_problems()
# print(problems)

# Process each problem
samples = []
for task_id in tqdm(problems):
    problem_info = problems[task_id]
    print(task_id)
    task_number = int(task_id.split('/')[1])
    if task_number < 480:
        continue
    prompt = problem_info['prompt']
    completion = solve_problem_with_llama(prompt)
    samples.append({
        "task_id": task_id,
        "completion": completion
    })
    write_jsonl("scot_mbpp_samples.jsonl", samples)
    samples = []



