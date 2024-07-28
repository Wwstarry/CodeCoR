from human_eval.data import write_jsonl, read_problems
import openai
from openai import OpenAI
import httpx
import re

 
pattern = r'```python(.*?)```'

sentence = """
Here is an output example.

def similar_elements(test_tup1, test_tup2):
    res = tuple(set(test_tup1) & set(test_tup2))
    return res
 
"""

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    # api_key="",
    http_client=httpx.Client(
        proxies="http://127.0.0.1:7890"
    )
)
 
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

samples = []
 
for task_id in problems:
    print(task_id)
 
    # prompt = problems[task_id]["text"] + '\nPlease cover all variables in the test case.' + ' '.join(problems[task_id]["test_list"]) + "Only provide the python code.Don't give examples and assertions."+sentence
    prompt = problems[task_id]["text"] +'Here is a kind of solution.\n'+' '.join(problems[task_id]["code"]) + "Only provide the python code.Don't give examples and assertions."+sentence

    # prompt ="Given the problem description and tests below, provide the Python code solution. "+\
    #        "No explanation or descriptive text is needed, just the code.\n"+\
    #         "Here is the real problem.\n "+problems[task_id]["text"]+'\n'+' '.join(problems[task_id]["code"])



    completion = generate_one_completion(prompt)
    
 
    completion_without_asserts = remove_asserts(completion)
    
    print(completion_without_asserts)
    
 
    samples.append({"task_id": task_id, "completion": completion})

write_jsonl("samples_mbpp_no_prompt.jsonl", samples)


# from human_eval.data import write_jsonl, read_problems
# import openai
# from openai import OpenAI
# import httpx
# import re

 
# pattern = r'```python(.*?)```'

# sentence = """
# Here is an output example.
# def similar_elements(test_tup1, test_tup2):
#     res = tuple(set(test_tup1) & set(test_tup2))
#     return res
# """

# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key="",
#     http_client=httpx.Client(
#         proxies="http://127.0.0.1:7890"
#     )
# )
 
# def generate_one_completion(prompt):
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt,
#             }
#         ],
#         model="gpt-3.5-turbo",
#     )

#     # print(chat_completion)
#     return chat_completion.choices.pop().message.content

# # print(generate_one_completion("hello"))



# problems = read_problems()

# print("read_problems is done!")

# samples = []
 
# for task_id in list(problems)[:5]:
#     print(task_id)
 
#     # prompt = problems[task_id]["text"] + '\nPlease cover all variables in the test case.' + ' '.join(problems[task_id]["test_list"]) + "Only provide the python code.Don't give examples and assertions."+sentence
#     prompt = problems[task_id]["text"] +'Here is a kind of solution.\n'+' '.join(problems[task_id]["code"])+ '\nPlease cover all variables in the test case.' + ' '.join(problems[task_id]["test_list"]) + "Only provide the python code.Don't give examples and assertions."+sentence

#     completion = generate_one_completion(prompt)
#     print(completion)
 
#     samples.append({"task_id": task_id, "completion": completion})

# write_jsonl("samples_mbpp_no_prompt.jsonl", samples)
 
# print(samples)

 
# write_jsonl("samples.jsonl", samples)
