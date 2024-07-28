import json


def extract_and_override_code(jsonl_file):
    with open(jsonl_file, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    for line in lines:
        data = json.loads(line)
        completion = data.get('completion', '')
        code_block = extract_code(completion)
        data['completion'] = code_block.strip() 
        modified_lines.append(json.dumps(data) + '\n')


    with open(jsonl_file, 'w') as file:
        file.writelines(modified_lines)



def extract_code(completion):
    start_index = completion.find('```python')
    end_index = completion.find('```', start_index + len('```python'))
    if start_index != -1 and end_index != -1:
        return completion[start_index:end_index].replace('```python', '')
    else:
        return ''



jsonl_file = 'samples_CoR.jsonl'
extract_and_override_code(jsonl_file)

print("Completion fields have been overwritten with pure code.")
