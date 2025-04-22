from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLWriter
from rasa.shared.nlu.training_data.training_data import TrainingData
import pandas as pd
# each data example has to be transformed into Message objects
intent_main_name = "all_main_item "
intent_business_name = "all_business_item "
intent_scenario_name = "all_scenario"
"""
    生成nlu的"区划'的训练数据
    """
df = pd.read_excel("source/import/excel_main0422.xlsx")
# df = pd.read_excel("source/nlu/不重复区划数据.xlsx")
 # 替换为你的文件名
print(df.columns.tolist())  # 查看所有列名
# 指定要处理的列名，例如 "模块名称"
column_list = ["区划名称"]
entity_dict = {"区划名称": "district",
               }
intent_dict = {"区划名称": "all_district_intent",
               }
for column in column_list:
    data = []
    # 获取该列的不重复值（去重）
    unique_values = df[column].dropna().unique()

    # 转为列表（可选）
    unique_values_list = unique_values.tolist()

    # 打印结果
    # print(f"{column_name} 不重复的值有：")
    for value in unique_values_list:
        # print(value)
        example1 = Message.build(text=value, intent=intent_dict[column], entities=[{
            "start": 0,
            "end": len(value),
            # "value": "数据分析",
            "entity": entity_dict[column]
        }])
        data.append(example1)
    # example2 = Message.build(text="hey", intent="greet")

    # pass the Message objects to the TrainingData
    td = TrainingData(data)

    # write to a yml file
    w1 = RasaYAMLWriter()
    f = w1.dump(f'data/business/{intent_dict[column]}.yml', td)
