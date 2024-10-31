
import json

def remove_cot_field(jsonl_file, output_file):
    with open(jsonl_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            
            if 'cot' in data:
                del data['cot']
            

            json.dump(data, outfile)
            outfile.write('\n')


remove_cot_field('codecot_cot_samples.jsonl', 'codecot_without_cot.jsonl')
