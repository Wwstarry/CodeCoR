import json

task_ids = [
    'Mbpp/163', 'Mbpp/228', 'Mbpp/246', 'Mbpp/248', 'Mbpp/291', 'Mbpp/304',
    'Mbpp/307', 'Mbpp/393', 'Mbpp/399', 'Mbpp/401', 'Mbpp/408', 'Mbpp/411',
    'Mbpp/417', 'Mbpp/434', 'Mbpp/443', 'Mbpp/444', 'Mbpp/452', 'Mbpp/464',
    'Mbpp/584', 'Mbpp/617', 'Mbpp/625', 'Mbpp/627', 'Mbpp/738', 'Mbpp/747',
    'Mbpp/756', 'Mbpp/776', 'Mbpp/779', 'Mbpp/802'
]




with open('', 'r') as file:
    lines = file.readlines()

filtered_lines = [line for line in lines if json.loads(line)['task_id'] not in task_ids]


with open('', 'w') as file:
    file.writelines(filtered_lines)
