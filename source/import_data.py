from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLWriter
from rasa.shared.nlu.training_data.training_data import TrainingData
import pandas as pd 
# each data example has to be transformed into Message objects
intent_main_name="all_main_item "
intent_business_name = "all_business_item "
intent_scenario_name = "all_scenario"

df = pd.read_excel("source/output.xlsx")  # 替换为你的文件名
print(df.columns.tolist())  # 查看所有列名
# 指定要处理的列名，例如 "模块名称"
column_list = ["主项名称",'业务办理项名称', '情形']
entity_dict = {"主项名称": "main_item",
               '业务办理项名称': "business_item", '情形': "scenario"}
intent_dict = {"主项名称": "all_main_item_intent",
               '业务办理项名称': "all_business_item_intent", '情形': "all_scenario_intent"}
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
