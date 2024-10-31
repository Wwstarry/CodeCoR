import json

def check_jsonl_file(file_path):
    with open(file_path, 'r') as file:
        line_number = 0
        for line in file:
            line_number += 1
            line = line.strip()  
            try:
                json.loads(line)  
            except json.JSONDecodeError as e:
                print(f"Invalid JSON at line {line_number}: {e}")
                return False
    print("All lines are valid JSON format.")
    return True


file_path = r'sample.jsonl'
check_jsonl_file(file_path)
