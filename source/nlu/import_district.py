from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLWriter
from rasa.shared.nlu.training_data.training_data import TrainingData
import pandas as pd
from tqdm import tqdm  # 导入进度条库

"""
    生成nlu的"区划名称"的训练数据，包含常规训练示例和lookup表
"""
df = pd.read_excel("source/import/excel_main0425.xlsx")
print("Excel列名:", df.columns.tolist())  # 查看所有列名

# 配置列名、实体和意图映射
column_list = ["区划名称"]
entity_dict = {"区划名称": "area"}
intent_dict = {"区划名称": "all_area_intent"}

for column in column_list:
    data = []
    lookup_data = []  # 存储lookup表数据

    # 获取该列的不重复值（去重）
    unique_values = df[column].dropna().unique()
    unique_values_list = unique_values.tolist()

    print(f"正在处理列: {column}, 共 {len(unique_values_list)} 个唯一值")

    # 使用进度条处理每个值
    for value in tqdm(unique_values_list, desc=f"处理 {column}"):
        if pd.isna(value):  # 跳过空值
            continue

        text = str(value).strip()

        # 添加常规训练示例
        example = Message.build(
            text=text,
            intent=intent_dict[column],
            entities=[{
                "start": 0,
                "end": len(text),
                "entity": entity_dict[column]
            }]
        )
        data.append(example)

        # 添加lookup表条目
        lookup_data.append(text)

    # 创建训练数据
    td = TrainingData(data)

    # 添加lookup表配置
    td.lookup_tables = [
        {
            "name": entity_dict[column],  # lookup表名称与实体名称一致
            "elements": lookup_data,     # 所有区划名称列表
            "elements_file": None       # 不使用外部文件
        }
    ]

    # 写入YAML文件
    w1 = RasaYAMLWriter()
    output_path = f'data/business/{intent_dict[column]}.yml'
    w1.dump(output_path, td)

    print(f"已生成文件: {output_path}")
    print(f"包含 {len(data)} 个训练示例和 {len(lookup_data)} 个lookup条目")

print("区划名称数据处理完成！")
