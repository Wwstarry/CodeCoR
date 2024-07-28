import json
import re

def extract_python_code(jsonl_file, output_file):
    pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    
    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            completion = data['completion']
            match = pattern.search(completion)
            if match:
                code_block = match.group(1).strip()
                data['completion'] = code_block
            json.dump(data, outfile)
            outfile.write('\n')


extract_python_code('self-planning_mbpp_samples.jsonl', 'self-planning_mbpp_modified_samples.jsonl')
