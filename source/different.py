import pandas as pd


def select_non_matching_field(input_file, output_file, field1, field2, selected_field):
    """
    读取Excel文件，比较两个字段，选择不相等的记录中的指定字段
    
    参数:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径
        field1: 第一个要比较的字段名
        field2: 第二个要比较的字段名
        selected_field: 要选择的字段名（当field1和field2不相等时）
    """
    # 读取Excel文件
    df = pd.read_excel(input_file)

    # 筛选出两个字段不相等的行
    non_matching = df[df[field1] != df[field2]]

    # 只保留选定的字段
    result = non_matching[selected_field]

    # 将结果保存到新的Excel文件
    result.to_excel(output_file, index=False)

    print(f"处理完成，结果已保存到 {output_file}")
    print(f"共找到 {len(non_matching)} 条不匹配的记录")


# 使用示例
if __name__ == "__main__":
    input_file = "source/main_item.xlsx"       # 输入Excel文件
    output_file = "output.xlsx"     # 输出Excel文件
    field1 = "主项名称"                # 第一个比较字段
    field2 = "业务办理项名称"                # 第二个比较字段
    selected_field = ["主项名称", "业务办理项名称", "情形"]        # 要选择的字段

    select_non_matching_field(input_file, output_file,
                              field1, field2, selected_field)
