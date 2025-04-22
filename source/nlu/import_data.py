from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLWriter
from rasa.shared.nlu.training_data.training_data import TrainingData
import pandas as pd
from tqdm import tqdm  # 导入进度条库

"""
    生成nlu的"主项名称",'业务办理项名称', '情形业务'的训练数据
"""
intent_main_name = "all_main_item "
intent_business_name = "all_business_item "
intent_scenario_name = "all_scenario"

# df = pd.read_excel("source/nlu/清洗后全市数据.xlsx")  # 替换为你的文件名
df = pd.read_excel("source/import/excel_main0422.xlsx")  # 替换为你的文件名
print("Excel列名:", df.columns.tolist())  # 查看所有列名

# 指定要处理的列名
column_list = ["主项名称", '业务办理项名称', '情形']
entity_dict = {"主项名称": "main_item",
               '业务办理项名称': "business_item", '情形': "scenario"}
intent_dict = {"主项名称": "all_main_item_intent",
               '业务办理项名称': "all_business_item_intent", '情形': "all_scenario_intent"}

# 添加总体进度条
with tqdm(column_list, desc="正在处理所有列", unit="column") as col_pbar:
    for column in col_pbar:
        col_pbar.set_postfix(column=column)  # 显示当前处理的列名
        data = []

        # 获取该列的不重复值（去重）
        unique_values = df[column].dropna().unique()
        unique_values_list = unique_values.tolist()

        # 添加值处理进度条
        with tqdm(unique_values_list, desc=f"处理 {column}", leave=False, unit="value") as val_pbar:
            for value in val_pbar:
                if pd.isna(value):  # 跳过空值
                    continue

                text = str(value).strip()
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
                val_pbar.set_postfix(
                    当前处理=text[:10]+"..." if len(text) > 10 else text)  # 显示当前处理的文本

        # 创建训练数据并保存
        td = TrainingData(data)
        w1 = RasaYAMLWriter()
        output_path = f'data/business/{intent_dict[column]}.yml'
        w1.dump(output_path, td)
        col_pbar.set_postfix(生成文件=output_path)  # 显示生成的文件路径

print("所有数据处理完成！")
