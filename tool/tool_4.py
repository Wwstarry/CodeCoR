import json

def replace_empty_completions(source_file, replacement_file, output_file):

    with open(source_file, 'r', encoding='utf-8') as src, open(replacement_file, 'r', encoding='utf-8') as repl:
        source_lines = src.readlines()
        replacement_lines = repl.readlines()
    
    if len(source_lines) != len(replacement_lines):
        raise ValueError("Source file and replacement file must have the same number of lines.")
    
    with open(output_file, 'w', encoding='utf-8') as out:
        for src_line, repl_line in zip(source_lines, replacement_lines):
            src_data = json.loads(src_line)
            repl_data = json.loads(repl_line)
            
            if src_data['completion'] == "":
                src_data['completion'] = repl_data['completion']
            
            json.dump(src_data, out)
            out.write('\n')


replace_empty_completions('scot_humaneval_samples.jsonl', 'cot_humaneval_samples.jsonl', 'output.jsonl')
