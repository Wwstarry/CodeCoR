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

    solving_process_prompt = """
Please understand the requirement and write a rough solving plan.And generate the code according to the plan. """ + """\n\n
Here are some examples:\n\n
Input：\n
prime_fib returns n-th number that is a Fibonacci number and it's also prime.

Output:\n
### Plan
1. Create a function to check if a number is prime.
2. Generate a Fibonacci sequence.
3. Check if each number in the Fibonacci sequence is prime,
decrement the counter.
4. If the counter is 0, return the Fibonacci number.

### Code
def prime_fib(n: int):
    def is_prime(n: int):
        '''
        is_prime returns True if n is prime, False otherwise.
        '''
        if n < 2:
            return False
        for i in range(2, n):
            if n % i == 0:
                return False
        return True
    fib_seq = [1, 1]
    counter = n
    while counter > 0:
        fib_seq.append(fib_seq[-1] + fib_seq[-2])
        if is_prime(fib_seq[-1]):
            counter -= 1
    return fib_seq[-1]

    """+"Here is the real input.\n"+prompt
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
    write_jsonl("self-planning_mbpp_samples.jsonl", samples)
    samples = []