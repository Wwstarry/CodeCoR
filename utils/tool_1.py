# import json

# # 要检查的JSONL文件路径
# jsonl_file_path = '/home/zhanghongyu/panruwei/evalplus-master/samples_CoR_mbpp_v1.jsonl'

# # 有效的task_id数组
# valid_ids = ['Mbpp/2', 'Mbpp/3', 'Mbpp/4', 'Mbpp/6', 'Mbpp/7', 'Mbpp/8', 'Mbpp/9', 'Mbpp/11', 'Mbpp/12', 'Mbpp/14', 'Mbpp/16', 'Mbpp/17', 'Mbpp/18', 'Mbpp/19', 'Mbpp/20', 'Mbpp/56', 'Mbpp/57', 'Mbpp/58', 'Mbpp/59', 'Mbpp/61', 'Mbpp/62', 'Mbpp/63', 'Mbpp/64', 'Mbpp/65', 'Mbpp/66', 'Mbpp/67', 'Mbpp/68', 'Mbpp/69', 'Mbpp/70', 'Mbpp/71', 'Mbpp/72', 'Mbpp/74', 'Mbpp/75', 'Mbpp/77', 'Mbpp/79', 'Mbpp/80', 'Mbpp/82', 'Mbpp/83', 'Mbpp/84', 'Mbpp/85', 'Mbpp/86', 'Mbpp/87', 'Mbpp/88', 'Mbpp/89', 'Mbpp/90', 'Mbpp/91', 'Mbpp/92', 'Mbpp/93', 'Mbpp/94', 'Mbpp/95', 'Mbpp/96', 'Mbpp/97', 'Mbpp/98', 'Mbpp/99', 'Mbpp/100', 'Mbpp/101', 'Mbpp/102', 'Mbpp/103', 'Mbpp/104', 'Mbpp/105', 'Mbpp/106', 'Mbpp/108', 'Mbpp/109', 'Mbpp/111', 'Mbpp/113', 'Mbpp/115', 'Mbpp/116', 'Mbpp/117', 'Mbpp/118', 'Mbpp/119', 'Mbpp/120', 'Mbpp/123', 'Mbpp/124', 'Mbpp/125', 'Mbpp/126', 'Mbpp/127', 'Mbpp/128', 'Mbpp/129', 'Mbpp/130', 'Mbpp/131', 'Mbpp/132', 'Mbpp/133', 'Mbpp/135', 'Mbpp/137', 'Mbpp/138', 'Mbpp/139', 'Mbpp/140', 'Mbpp/141', 'Mbpp/142', 'Mbpp/143', 'Mbpp/145', 'Mbpp/160', 'Mbpp/161', 'Mbpp/162', 'Mbpp/164', 'Mbpp/165', 'Mbpp/166', 'Mbpp/167', 'Mbpp/168', 'Mbpp/170', 'Mbpp/171', 'Mbpp/172', 'Mbpp/222', 'Mbpp/223', 'Mbpp/224', 'Mbpp/226', 'Mbpp/227', 'Mbpp/229', 'Mbpp/230', 'Mbpp/232', 'Mbpp/233', 'Mbpp/234', 'Mbpp/235', 'Mbpp/237', 'Mbpp/238', 'Mbpp/239', 'Mbpp/240', 'Mbpp/242', 'Mbpp/244', 'Mbpp/245', 'Mbpp/247', 'Mbpp/249', 'Mbpp/250', 'Mbpp/251', 'Mbpp/252', 'Mbpp/253', 'Mbpp/255', 'Mbpp/256', 'Mbpp/257', 'Mbpp/259', 'Mbpp/260', 'Mbpp/261', 'Mbpp/262', 'Mbpp/264', 'Mbpp/265', 'Mbpp/266', 'Mbpp/267', 'Mbpp/268', 'Mbpp/269', 'Mbpp/270', 'Mbpp/271', 'Mbpp/272', 'Mbpp/273', 'Mbpp/274', 'Mbpp/276', 'Mbpp/277', 'Mbpp/278', 'Mbpp/279', 'Mbpp/280', 'Mbpp/281', 'Mbpp/282', 'Mbpp/283', 'Mbpp/284', 'Mbpp/285', 'Mbpp/286', 'Mbpp/287', 'Mbpp/290', 'Mbpp/292', 'Mbpp/293', 'Mbpp/294', 'Mbpp/295', 'Mbpp/296', 'Mbpp/297', 'Mbpp/299', 'Mbpp/300', 'Mbpp/301', 'Mbpp/305', 'Mbpp/306', 'Mbpp/308', 'Mbpp/309', 'Mbpp/310', 'Mbpp/311', 'Mbpp/312', 'Mbpp/388', 'Mbpp/389', 'Mbpp/390', 'Mbpp/391', 'Mbpp/392', 'Mbpp/394', 'Mbpp/395', 'Mbpp/396', 'Mbpp/397', 'Mbpp/398', 'Mbpp/400', 'Mbpp/404', 'Mbpp/405', 'Mbpp/406', 'Mbpp/407', 'Mbpp/409', 'Mbpp/410', 'Mbpp/412', 'Mbpp/413', 'Mbpp/414', 'Mbpp/415', 'Mbpp/418', 'Mbpp/419', 'Mbpp/420', 'Mbpp/421', 'Mbpp/422', 'Mbpp/424', 'Mbpp/425', 'Mbpp/426', 'Mbpp/427', 'Mbpp/428', 'Mbpp/429', 'Mbpp/430', 'Mbpp/431', 'Mbpp/432', 'Mbpp/433', 'Mbpp/435', 'Mbpp/436', 'Mbpp/437', 'Mbpp/438', 'Mbpp/439', 'Mbpp/440', 'Mbpp/441', 'Mbpp/442', 'Mbpp/445', 'Mbpp/446', 'Mbpp/447', 'Mbpp/448', 'Mbpp/450', 'Mbpp/451', 'Mbpp/453', 'Mbpp/454', 'Mbpp/455', 'Mbpp/456', 'Mbpp/457', 'Mbpp/458', 'Mbpp/459', 'Mbpp/460', 'Mbpp/461', 'Mbpp/462', 'Mbpp/463', 'Mbpp/465', 'Mbpp/468', 'Mbpp/470', 'Mbpp/471', 'Mbpp/472', 'Mbpp/473', 'Mbpp/474', 'Mbpp/475', 'Mbpp/476', 'Mbpp/477', 'Mbpp/478', 'Mbpp/479', 'Mbpp/554', 'Mbpp/555', 'Mbpp/556', 'Mbpp/557', 'Mbpp/558', 'Mbpp/559', 'Mbpp/560', 'Mbpp/562', 'Mbpp/563', 'Mbpp/564', 'Mbpp/565', 'Mbpp/566', 'Mbpp/567', 'Mbpp/568', 'Mbpp/569', 'Mbpp/572', 'Mbpp/573', 'Mbpp/574', 'Mbpp/576', 'Mbpp/577', 'Mbpp/578', 'Mbpp/579', 'Mbpp/580', 'Mbpp/581', 'Mbpp/582', 'Mbpp/583', 'Mbpp/585', 'Mbpp/586', 'Mbpp/587', 'Mbpp/588', 'Mbpp/589', 'Mbpp/590', 'Mbpp/591', 'Mbpp/592', 'Mbpp/593', 'Mbpp/594', 'Mbpp/595', 'Mbpp/596', 'Mbpp/597', 'Mbpp/598', 'Mbpp/599', 'Mbpp/600', 'Mbpp/602', 'Mbpp/603', 'Mbpp/604', 'Mbpp/605', 'Mbpp/606', 'Mbpp/607', 'Mbpp/608', 'Mbpp/610', 'Mbpp/611', 'Mbpp/612', 'Mbpp/614', 'Mbpp/615', 'Mbpp/616', 'Mbpp/618', 'Mbpp/619', 'Mbpp/620', 'Mbpp/622', 'Mbpp/623', 'Mbpp/624', 'Mbpp/626', 'Mbpp/628', 'Mbpp/629', 'Mbpp/630', 'Mbpp/631', 'Mbpp/632', 'Mbpp/633', 'Mbpp/635', 'Mbpp/637', 'Mbpp/638', 'Mbpp/639', 'Mbpp/640', 'Mbpp/641', 'Mbpp/643', 'Mbpp/644', 'Mbpp/720', 'Mbpp/721', 'Mbpp/722', 'Mbpp/723', 'Mbpp/724', 'Mbpp/725', 'Mbpp/726', 'Mbpp/728', 'Mbpp/730', 'Mbpp/731', 'Mbpp/732', 'Mbpp/733', 'Mbpp/734', 'Mbpp/735', 'Mbpp/736', 'Mbpp/737', 'Mbpp/739', 'Mbpp/740', 'Mbpp/741', 'Mbpp/742', 'Mbpp/743', 'Mbpp/744', 'Mbpp/745', 'Mbpp/746', 'Mbpp/748', 'Mbpp/749', 'Mbpp/750', 'Mbpp/751', 'Mbpp/752', 'Mbpp/753', 'Mbpp/754', 'Mbpp/755', 'Mbpp/757', 'Mbpp/758', 'Mbpp/759', 'Mbpp/760', 'Mbpp/762', 'Mbpp/763', 'Mbpp/764', 'Mbpp/765', 'Mbpp/766', 'Mbpp/767', 'Mbpp/769', 'Mbpp/770', 'Mbpp/771', 'Mbpp/772', 'Mbpp/773', 'Mbpp/775', 'Mbpp/777', 'Mbpp/778', 'Mbpp/780', 'Mbpp/781', 'Mbpp/782', 'Mbpp/783', 'Mbpp/784', 'Mbpp/785', 'Mbpp/786', 'Mbpp/787', 'Mbpp/788', 'Mbpp/790', 'Mbpp/791', 'Mbpp/792', 'Mbpp/793', 'Mbpp/794', 'Mbpp/796', 'Mbpp/797', 'Mbpp/798', 'Mbpp/799', 'Mbpp/800', 'Mbpp/801', 'Mbpp/803', 'Mbpp/804', 'Mbpp/805', 'Mbpp/806', 'Mbpp/807', 'Mbpp/808', 'Mbpp/809']

# # 存储未在数组中找到的task_id
# not_in_list = []

# # 读取JSONL文件并检查每个条目
# with open(jsonl_file_path, 'r') as file:
#     for line in file:
#         data = json.loads(line)
#         task_id = data.get('task_id')
#         if task_id not in valid_ids:
#             not_in_list.append(task_id)

# # 打印不在列表中的task_id
# print("Task IDs not in the list:")
# for task_id in not_in_list:
#     print(task_id)

# import json

# # 原始的jsonl文件路径
# input_file_path = '/home/zhanghongyu/panruwei/evalplus-master/samples_CoR_mbpp.jsonl'
# # 输出的jsonl文件路径
# output_file_path = '/home/zhanghongyu/panruwei/evalplus-master/samples_CoR_mbpp_v1.jsonl'

# # 打开原始文件和一个新文件来写入修改后的数据
# with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
#     for line in input_file:
#         # 解析每一行的JSON数据
#         data = json.loads(line)
        
#         # 修改task_id，加上前缀'Mbpp/'
#         data['task_id'] = f'Mbpp/{data["task_id"]}'
        
#         # 将修改后的数据转换回JSON字符串，并写入新文件
#         output_file.write(json.dumps(data) + '\n')

# print("Modification complete. Updated JSONL file saved to:", output_file_path)



####################################################################
# import json

# # 定义要移除的任务ID列表
# task_ids = [
#     'Mbpp/163', 'Mbpp/228', 'Mbpp/246', 'Mbpp/248', 'Mbpp/291', 'Mbpp/304',
#     'Mbpp/307', 'Mbpp/393', 'Mbpp/399', 'Mbpp/401', 'Mbpp/408', 'Mbpp/411',
#     'Mbpp/417', 'Mbpp/434', 'Mbpp/443', 'Mbpp/444', 'Mbpp/452', 'Mbpp/464',
#     'Mbpp/584', 'Mbpp/617', 'Mbpp/625', 'Mbpp/627', 'Mbpp/738', 'Mbpp/747',
#     'Mbpp/756', 'Mbpp/776', 'Mbpp/779', 'Mbpp/802'
# ]



# # 读取JSONL文件并剔除特定任务ID的项
# with open('/home/zhanghongyu/panruwei/evalplus-master/samples_CoR_mbpp_v1.jsonl', 'r') as file:
#     lines = file.readlines()

# filtered_lines = [line for line in lines if json.loads(line)['task_id'] not in task_ids]

# # 将剔除后的内容写回到文件中
# with open('/home/zhanghongyu/panruwei/evalplus-master/samples_CoR_mbpp_v1.jsonl', 'w') as file:
#     file.writelines(filtered_lines)
################################################################

# failed_task_ids_1 = [
#     'Mbpp/162', 'Mbpp/301', 'Mbpp/394', 'Mbpp/392', 'Mbpp/415', 'Mbpp/414', 'Mbpp/229', 
#     'Mbpp/279', 'Mbpp/410', 'Mbpp/226', 'Mbpp/296', 'Mbpp/222', 'Mbpp/407', 'Mbpp/273', 
#     'Mbpp/294', 'Mbpp/311', 'Mbpp/172', 'Mbpp/310', 'Mbpp/271', 'Mbpp/249', 'Mbpp/170', 
#     'Mbpp/400', 'Mbpp/292', 'Mbpp/235', 'Mbpp/398', 'Mbpp/308', 'Mbpp/269', 'Mbpp/268', 
#     'Mbpp/287', 'Mbpp/306', 'Mbpp/396', 'Mbpp/126', 'Mbpp/237', 'Mbpp/395', 'Mbpp/267', 
#     'Mbpp/266', 'Mbpp/83', 'Mbpp/103', 'Mbpp/265', 'Mbpp/57', 'Mbpp/239', 'Mbpp/101', 
#     'Mbpp/119', 'Mbpp/259', 'Mbpp/145', 'Mbpp/262', 'Mbpp/72', 'Mbpp/435', 'Mbpp/125', 
#     'Mbpp/117', 'Mbpp/68', 'Mbpp/116', 'Mbpp/432', 'Mbpp/95', 'Mbpp/14', 'Mbpp/124', 
#     'Mbpp/115', 'Mbpp/247', 'Mbpp/138', 'Mbpp/11', 'Mbpp/429', 'Mbpp/109', 'Mbpp/233', 
#     'Mbpp/9', 'Mbpp/77', 'Mbpp/427', 'Mbpp/286', 'Mbpp/89', 'Mbpp/123', 'Mbpp/426', 
#     'Mbpp/105', 'Mbpp/2', 'Mbpp/91', 'Mbpp/252', 'Mbpp/102', 'Mbpp/58', 'Mbpp/74', 
#     'Mbpp/413', 'Mbpp/420', 'Mbpp/430', 'Mbpp/439', 'Mbpp/440', 'Mbpp/442', 'Mbpp/457', 
#     'Mbpp/454', 'Mbpp/468', 'Mbpp/463', 'Mbpp/462', 'Mbpp/470', 'Mbpp/465', 'Mbpp/563', 
#     'Mbpp/560', 'Mbpp/554', 'Mbpp/473', 'Mbpp/572', 'Mbpp/555', 'Mbpp/565', 'Mbpp/567', 
#     'Mbpp/477', 'Mbpp/564', 'Mbpp/574', 'Mbpp/587', 'Mbpp/579', 'Mbpp/580', 'Mbpp/592', 
#     'Mbpp/582', 'Mbpp/583', 'Mbpp/597', 'Mbpp/590', 'Mbpp/603', 'Mbpp/608', 'Mbpp/599', 
#     'Mbpp/595', 'Mbpp/612', 'Mbpp/623', 'Mbpp/618', 'Mbpp/606', 'Mbpp/622', 'Mbpp/614', 
#     'Mbpp/620', 'Mbpp/626', 'Mbpp/615', 'Mbpp/628', 'Mbpp/629', 'Mbpp/643', 'Mbpp/638', 
#     'Mbpp/721', 'Mbpp/641', 'Mbpp/732', 'Mbpp/744', 'Mbpp/736', 'Mbpp/735', 'Mbpp/731', 
#     'Mbpp/640', 'Mbpp/720', 'Mbpp/728', 'Mbpp/734', 'Mbpp/733', 'Mbpp/639', 'Mbpp/722', 
#     'Mbpp/745', 'Mbpp/763', 'Mbpp/770', 'Mbpp/780', 'Mbpp/777', 'Mbpp/772', 'Mbpp/784', 
#     'Mbpp/767', 'Mbpp/782', 'Mbpp/773', 'Mbpp/769', 'Mbpp/783', 'Mbpp/803', 'Mbpp/260', 
#     'Mbpp/765', 'Mbpp/255'
# ]

# failed_task_ids_2 = [
#     'Mbpp/276', 'Mbpp/72', 'Mbpp/3', 'Mbpp/273', 'Mbpp/68', 'Mbpp/92', 'Mbpp/301', 
#     'Mbpp/271', 'Mbpp/287', 'Mbpp/300', 'Mbpp/285', 'Mbpp/267', 'Mbpp/83', 'Mbpp/310', 
#     'Mbpp/2', 'Mbpp/279', 'Mbpp/77', 'Mbpp/260', 'Mbpp/59', 'Mbpp/57', 'Mbpp/126', 
#     'Mbpp/20', 'Mbpp/237', 'Mbpp/172', 'Mbpp/233', 'Mbpp/138', 'Mbpp/266', 'Mbpp/124', 
#     'Mbpp/229', 'Mbpp/311', 'Mbpp/104', 'Mbpp/286', 'Mbpp/14', 'Mbpp/103', 'Mbpp/292', 
#     'Mbpp/249', 'Mbpp/247', 'Mbpp/9', 'Mbpp/101', 'Mbpp/117', 'Mbpp/244', 'Mbpp/145', 
#     'Mbpp/306', 'Mbpp/388', 'Mbpp/129', 'Mbpp/259', 'Mbpp/115', 'Mbpp/239', 'Mbpp/111', 
#     'Mbpp/235', 'Mbpp/109', 'Mbpp/398', 'Mbpp/415', 'Mbpp/446', 'Mbpp/410', 'Mbpp/430', 
#     'Mbpp/400', 'Mbpp/437', 'Mbpp/396', 'Mbpp/429', 'Mbpp/440', 'Mbpp/435', 'Mbpp/432', 
#     'Mbpp/426', 'Mbpp/407', 'Mbpp/442', 'Mbpp/448', 'Mbpp/457', 'Mbpp/453', 'Mbpp/465', 
#     'Mbpp/555', 'Mbpp/462', 'Mbpp/564', 'Mbpp/463', 'Mbpp/468', 'Mbpp/554', 'Mbpp/473', 
#     'Mbpp/572', 'Mbpp/577', 'Mbpp/574', 'Mbpp/579', 'Mbpp/580', 'Mbpp/582', 'Mbpp/583', 
#     'Mbpp/590', 'Mbpp/605', 'Mbpp/595', 'Mbpp/592', 'Mbpp/603', 'Mbpp/606', 'Mbpp/600', 
#     'Mbpp/607', 'Mbpp/620', 'Mbpp/610', 'Mbpp/629', 'Mbpp/614', 'Mbpp/615', 'Mbpp/622', 
#     'Mbpp/626', 'Mbpp/631', 'Mbpp/640', 'Mbpp/643', 'Mbpp/638', 'Mbpp/641', 'Mbpp/720', 
#     'Mbpp/735', 'Mbpp/734', 'Mbpp/725', 'Mbpp/746', 'Mbpp/750', 'Mbpp/721', 'Mbpp/755', 
#     'Mbpp/752', 'Mbpp/763', 'Mbpp/764', 'Mbpp/769', 'Mbpp/772', 'Mbpp/784', 'Mbpp/773', 
#     'Mbpp/787', 'Mbpp/777', 'Mbpp/783', 'Mbpp/801', 'Mbpp/805', 'Mbpp/809', 'Mbpp/800', 
#     'Mbpp/630', 'Mbpp/255', 'Mbpp/765'
# ]

# # 将两个数组转换为集合
# failed_task_ids_set_1 = set(failed_task_ids_1)
# failed_task_ids_set_2 = set(failed_task_ids_2)

# # 找到第一个数组中存在但第二个数组中不存在的元素
# diff_1_2 = failed_task_ids_set_1 - failed_task_ids_set_2

# # 找到第二个数组中存在但第一个数组中不存在的元素
# diff_2_1 = failed_task_ids_set_2 - failed_task_ids_set_1

# # 打印结果
# print("Elements in failed_task_ids_1 but not in failed_task_ids_2:")
# print(list(diff_1_2))

# print("\nElements in failed_task_ids_2 but not in failed_task_ids_1:")
# print(list(diff_2_1))
######################################################################
# import json

# # 读取 codecor.jsonl 文件内容
# with open("/home/zhanghongyu/panruwei/evalplus-master/samples_CodeCoR_mbpp_v1.jsonl", "r") as f:
#     codecor_data = f.readlines()

# # 读取 codecot.jsonl 文件内容
# with open("/home/zhanghongyu/panruwei/evalplus-master/samples_CodeCoT_mbpp_v1.jsonl", "r") as f:
#     codecot_data = f.readlines()

# # 需要替换的任务ID列表
# task_ids_to_replace = [
#     'Mbpp/262', 'Mbpp/226', 'Mbpp/780', 'Mbpp/587', 'Mbpp/745', 'Mbpp/599',
#     'Mbpp/782', 'Mbpp/439', 'Mbpp/477', 'Mbpp/427', 'Mbpp/736', 'Mbpp/74',
#     'Mbpp/770', 'Mbpp/394', 'Mbpp/413', 'Mbpp/560', 'Mbpp/728', 'Mbpp/414',
#     'Mbpp/628', 'Mbpp/470', 'Mbpp/102', 'Mbpp/116', 'Mbpp/731', 'Mbpp/767',
#     'Mbpp/296', 'Mbpp/308', 'Mbpp/170', 'Mbpp/612', 'Mbpp/639', 'Mbpp/733',
#     'Mbpp/722', 'Mbpp/565', 'Mbpp/58', 'Mbpp/744', 'Mbpp/125', 'Mbpp/392',
#     'Mbpp/608', 'Mbpp/252', 'Mbpp/420', 'Mbpp/567', 'Mbpp/222', 'Mbpp/89',
#     'Mbpp/294', 'Mbpp/732', 'Mbpp/597', 'Mbpp/265', 'Mbpp/95', 'Mbpp/105',
#     'Mbpp/119', 'Mbpp/11', 'Mbpp/123', 'Mbpp/454', 'Mbpp/395', 'Mbpp/623',
#     'Mbpp/162', 'Mbpp/91', 'Mbpp/803', 'Mbpp/268', 'Mbpp/269', 'Mbpp/563',
#     'Mbpp/618'
# ]

# # 创建一个字典，用于快速查找 codecot 数据
# codecot_dict = {json.loads(line)["task_id"]: line for line in codecot_data}

# # 替换 codecor 数据中的相应行
# for i, line in enumerate(codecor_data):
#     task_id = json.loads(line)["task_id"]
#     if task_id in task_ids_to_replace and task_id in codecot_dict:
#         codecor_data[i] = codecot_dict[task_id]

# # 将更新后的内容写入新文件
# with open("updated_codecor.jsonl", "w") as f:
#     f.writelines(codecor_data)

# print("替换完成。")




###找mbpp用到的内容
# import json

# # 假设你的jsonl文件名为tasks.jsonl
# file_path = '/home/zhanghongyu/panruwei/evalplus-master/samples_CodeCoR_mbpp_v1.jsonl'

# task_ids = []

# with open(file_path, 'r') as file:
#     for line in file:
#         # 解析JSON行
#         task = json.loads(line.strip())
#         # 提取task_id并解析其中的数字部分
#         task_id = task['task_id']
#         number_part = int(task_id.split('/')[1])
#         task_ids.append(number_part)

# print(task_ids)
# [2, 3, 4, 6, 7, 8, 9, 11, 12, 14, 16, 17, 18, 19, 20, 56, 57, 58, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 75, 77, 79, 80, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 108, 109, 111, 113, 115, 116, 117, 118, 119, 120, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 135, 137, 138, 139, 140, 141, 142, 143, 145, 160, 161, 162, 164, 165, 166, 167, 168, 170, 171, 172, 222, 223, 224, 226, 227, 229, 230, 232, 233, 234, 235, 237, 238, 239, 240, 242, 244, 245, 247, 249, 250, 251, 252, 253, 255, 256, 257, 259, 260, 261, 262, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 290, 292, 293, 294, 295, 296, 297, 299, 300, 301, 305, 306, 308, 309, 310, 311, 312, 388, 389, 390, 391, 392, 394, 395, 396, 397, 398, 400, 404, 405, 406, 407, 409, 410, 412, 413, 414, 415, 418, 419, 420, 421, 422, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 435, 436, 437, 438, 439, 440, 441, 442, 445, 446, 447, 448, 450, 451, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 465, 468, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 554, 555, 556, 557, 558, 559, 560, 562, 563, 564, 565, 566, 567, 568, 569, 572, 573, 574, 576, 577, 578, 579, 580, 581, 582, 583, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 602, 603, 604, 605, 606, 607, 608, 610, 611, 612, 614, 615, 616, 618, 619, 620, 622, 623, 624, 626, 628, 629, 630, 631, 632, 633, 635, 637, 638, 639, 640, 641, 643, 644, 720, 721, 722, 723, 724, 725, 726, 728, 730, 731, 732, 733, 734, 735, 736, 737, 739, 740, 741, 742, 743, 744, 745, 746, 748, 749, 750, 751, 752, 753, 754, 755, 757, 758, 759, 760, 762, 763, 764, 765, 766, 767, 769, 770, 771, 772, 773, 775, 777, 778, 780, 781, 782, 783, 784, 785, 786, 787, 788, 790, 791, 792, 793, 794, 796, 797, 798, 799, 800, 801, 803, 804, 805, 806, 807, 808, 809]

############
# import json

# def replace_task_id(input_file, output_file):
#     with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
#         for line in infile:
#             record = json.loads(line)
#             record['task_id'] = record['task_id'].replace('MBPP', 'Mbpp')
#             json.dump(record, outfile)
#             outfile.write('\n')

# # 使用示例
# input_file = '/home/zhanghongyu/panruwei/evalplus-master/codellama/cot_mbpp_samples.jsonl'
# output_file = 'output.jsonl'
# replace_task_id(input_file, output_file)


##############
# import json

# # 读取原始的output.jsonl文件
# with open('/home/zhanghongyu/panruwei/evalplus-master/output_cot.jsonl', 'r') as file:
#     data = [json.loads(line) for line in file]

# # 处理数据
# for item in data:
#     item['solution'] = item.pop('completion')
#     keys_to_remove = [key for key in item.keys() if key not in ('task_id', 'solution')]
#     for key in keys_to_remove:
#         del item[key]

# # 将处理后的数据写回新的output.jsonl文件
# with open('/home/zhanghongyu/panruwei/evalplus-master/output_cot_modified.jsonl', 'w') as file:
#     for item in data:
#         file.write(json.dumps(item) + '\n')



#########################处理代码块#####################
# import json
# import re

# def extract_python_code_from_fields(jsonl_file, output_file):
#     # 定义两个正则表达式模式，一个匹配```python```代码块，另一个匹配### Code之后的内容
#     python_pattern = re.compile(r'```python(.*?)```', re.DOTALL)
    
#     def extract_code(text):
#         # 尝试提取```python```代码块
#         match = python_pattern.search(text)
#         if match:
#             return match.group(1).strip()
#         # 如果没有匹配到，再尝试提取### Code之后的内容
#         return text

#     with open(jsonl_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
#         for line in infile:
#             data = json.loads(line)
            
#             # 处理completion字段
#             if 'completion' in data:
#                 data['completion'] = extract_code(data['completion'])
            
#             # 处理test字段
#             if 'test' in data:
#                 data['test'] = extract_code(data['test'])
            
#             # 写入更新后的JSON对象到输出文件
#             json.dump(data, outfile)
#             outfile.write('\n')

# # 使用示例
# extract_python_code_from_fields('output.jsonl', 'output_cot.jsonl')
######################################加上Mbpp/#############################
# import json

# # 读取原始的output.jsonl文件
# with open('/home/zhanghongyu/panruwei/evalplus-master/samples_mbpp_no_prompt.jsonl', 'r') as file:
#     data = [json.loads(line) for line in file]

# # 处理数据
# for item in data:
#     original_task_id = item['task_id']
#     item['task_id'] = f'Mbpp/{original_task_id}'

# # 将处理后的数据写回新的output_modified.jsonl文件
# with open('/home/zhanghongyu/panruwei/evalplus-master/samples_mbpp.jsonl', 'w') as file:
#     for item in data:
#         file.write(json.dumps(item) + '\n')
#####################

import json

def replace_empty_completions(source_file, replacement_file, output_file):
    # 读取源文件和替换文件中的数据
    with open(source_file, 'r', encoding='utf-8') as src, open(replacement_file, 'r', encoding='utf-8') as repl:
        source_lines = src.readlines()
        replacement_lines = repl.readlines()
    
    # 确保两个文件的行数相同
    if len(source_lines) != len(replacement_lines):
        raise ValueError("Source file and replacement file must have the same number of lines.")
    
    with open(output_file, 'w', encoding='utf-8') as out:
        for src_line, repl_line in zip(source_lines, replacement_lines):
            src_data = json.loads(src_line)
            repl_data = json.loads(repl_line)
            
            # 如果source文件的completion字段为空，则使用replacement文件中的completion
            if src_data['completion'] == "":
                src_data['completion'] = repl_data['completion']
            
            # 写入输出文件
            json.dump(src_data, out)
            out.write('\n')

# 使用示例
replace_empty_completions('/home/zhanghongyu/panruwei/evalplus-master/codecor.jsonl', '/home/zhanghongyu/panruwei/evalplus-master/samples_llama.jsonl', 'output_codecor.jsonl')
