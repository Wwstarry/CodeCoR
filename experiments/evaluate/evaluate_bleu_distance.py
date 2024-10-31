import jsonlines
import editdistance
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def read_jsonl(file_path):
    data = []
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            data.append(obj)
    return data

def calculate_edit_distance(generated_code, reference_code):
    return editdistance.eval(generated_code, reference_code)

def calculate_bleu_score(generated_code, reference_code):
    smoothie = SmoothingFunction().method4
    reference_tokens = [list(reference_code)]
    generated_tokens = list(generated_code)
    return sentence_bleu(reference_tokens, generated_tokens, smoothing_function=smoothie)

def main():
    reference_file = 'MBPP_sanitized.jsonl' 
    generated_file = 'samples_CodeCoR_mbpp_v1.jsonl'

    reference_data = read_jsonl(reference_file)
    generated_data = read_jsonl(generated_file)

    total_edit_distance = 0
    total_bleu_score = 0
    num_samples = len(reference_data)

    for ref, gen in zip(reference_data, generated_data):
        if ref['task_id'] != gen['task_id']:
            print(f"Task ID mismatch: {ref['task_id']} != {gen['task_id']}")
            continue

        reference_code = ref['canonical_solution']
        generated_code = gen['solution']

        edit_distance = calculate_edit_distance(generated_code, reference_code)
        bleu_score = calculate_bleu_score(generated_code, reference_code)

        total_edit_distance += edit_distance
        total_bleu_score += bleu_score


        print(f"Task ID: {ref['task_id']}")
        print(f"Edit Distance: {edit_distance}")
        print(f"BLEU Score: {bleu_score}\n")

    average_edit_distance = total_edit_distance / num_samples
    average_bleu_score = total_bleu_score / num_samples

    print(f"Average Edit Distance: {average_edit_distance}")
    print(f"Average BLEU Score: {average_bleu_score}")

if __name__ == "__main__":
    main()



