import pandas as pd







def check_field_inclusion(excel_file, column1, column2, sheet_name=0):
    """
    检查Excel文件中两个字段的包含关系
    
    参数:
        excel_file (str): Excel文件路径
        column1 (str): 第一个字段名
        column2 (str): 第二个字段名
        sheet_name (str/int): 工作表名称或索引，默认为第一个工作表
    
    返回:
        DataFrame: 包含检查结果的DataFrame
    """
    # 读取Excel文件
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
    except Exception as e:
        print(f"读取文件出错: {e}")
        return None

    # 检查字段是否存在
    if column1 not in df.columns or column2 not in df.columns:
        print(f"错误: 指定的字段 '{column1}' 或 '{column2}' 不存在")
        return None

    # 创建新列存储检查结果
    df[f'{column1}_包含_{column2}'] = df.apply(
        lambda row: str(row[column2]) in str(row[column1]) if pd.notna(
            row[column1]) and pd.notna(row[column2]) else False,
        axis=1
    )

    df[f'{column2}_包含_{column1}'] = df.apply(
        lambda row: str(row[column1]) in str(row[column2]) if pd.notna(
            row[column1]) and pd.notna(row[column2]) else False,
        axis=1
    )

    # 筛选出满足任一包含条件的记录
    included_records = df[df[f'{column1}_包含_{column2}']
                          | df[f'{column2}_包含_{column1}']].copy()

    # 添加关系类型列
    included_records['包含关系'] = included_records.apply(
        lambda row: f"{column1}包含{column2}" if row[f'{column1}_包含_{column2}'] else f"{column2}包含{column1}",
        axis=1
    )

    return included_records


# 使用示例
if __name__ == "__main__":
    # 替换为你的Excel文件路径和字段名


    file_path = "source/import/excel_main0425.xlsx"
    col1 = "主项名称"
    col2 = "业务办理项名称"

    result = check_field_inclusion(file_path, col1, col2)

    if result is not None:
        # 打印结果
        print("找到包含关系的记录：")
        print(result[[col1, col2, '包含关系']])

        # 保存结果到新Excel文件
        output_file = "inclusion_results.xlsx"
        result.to_excel(output_file, index=False)
        print(f"\n检查结果已保存到: {output_file}")

        # 统计结果
        print("\n包含关系统计：")
        print(result['包含关系'].value_counts())
