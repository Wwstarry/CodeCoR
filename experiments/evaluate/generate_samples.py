from human_eval.data import write_jsonl, read_problems

def generate_one_completion(prompt):
    # 在提示后添加一些文本
    return prompt + " This is a generated completion."

problems = read_problems()

num_samples_per_task = 200
samples = [
    dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
    for task_id in problems
    for _ in range(num_samples_per_task)
]
write_jsonl("samples.jsonl", samples)
