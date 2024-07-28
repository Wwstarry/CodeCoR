import subprocess
import sys

python_files = [
    'self-planning_call.py',
    'scot_call.py'
    'cot_call.py',
    'codecot.py'

]

for python_file in python_files:
    try:
        result = subprocess.run([sys.executable, python_file], check=True, stderr=subprocess.PIPE)
        print(f"Successfully ran {python_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run {python_file}")
        print("Errors:\n", e.stderr.decode())
