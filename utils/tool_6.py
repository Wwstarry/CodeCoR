import json
import re

def extract_python_code_from_fields(jsonl_file, output_file):

    python_pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    
    def extract_code(text):

        match = python_pattern.search(text)
        if match:
            return match.group(1).strip()

        return text

    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            

            if 'completion' in data:
                data['completion'] = extract_code(data['completion'])
            

            if 'test' in data:
                data['test'] = extract_code(data['test'])
            

            json.dump(data, outfile)
            outfile.write('\n')


extract_python_code_from_fields('codecot_without_cot.jsonl', 'codecot_humaneval_samples.jsonl')
