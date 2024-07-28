###this code doesn't work, we use another. 

import json

def extract_tests_from_jsonl(file_path):
    """
    Extract tests from a JSON Lines file.

    Args:
    file_path (str): The path to the JSON Lines file.

    Returns:
    dict: A dictionary with task_id as keys and test code as values.
    """
    tests = {}
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            task_id = data.get("task_id")
            test = data.get("test")
            if task_id and test:
                tests[task_id] = test
    return tests

def extract_completions_from_jsonl(file_path):
    """
    Extract code completions from a JSON Lines file.

    Args:
    file_path (str): The path to the JSON Lines file.

    Returns:
    dict: A dictionary with task_id as keys and code completion as values.
    """
    completions = {}
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            task_id = data.get("task_id")
            completion = data.get("completion")
            if task_id and completion:
                completions[task_id] = completion
    return completions

def run_tests_and_calculate_accuracy(tests, completions):
    """
    Run the tests and calculate the accuracy of the code completions.

    Args:
    tests (dict): A dictionary with task_id as keys and test code as values.
    completions (dict): A dictionary with task_id as keys and code completion as values.

    Returns:
    float: The accuracy of the code completions.
    """
    total_tests = len(tests)
    correct_tests = 0
    for task_id, test in tests.items():
        completion = completions.get(task_id)
        if completion:
            try:
                exec(completion)  # Execute the code completion
                exec(test)  # Execute the test case
                exec("check(min_cost)")  # Assume there is a check function to validate the result
                correct_tests += 1
            except:
                pass
    accuracy = correct_tests / total_tests if total_tests > 0 else 0
    return accuracy

# Paths to the test cases and code completions JSON Lines files
test_file_path = "path_to_test_file.jsonl"  # Replace with your test file path
completion_file_path = "path_to_completion_file.jsonl"  # Replace with your completion file path

# Extract tests and code completions
tests = extract_tests_from_jsonl(test_file_path)
completions = extract_completions_from_jsonl(completion_file_path)

# Run the tests and calculate the accuracy
accuracy = run_tests_and_calculate_accuracy(tests, completions)
print("Accuracy:", accuracy)
