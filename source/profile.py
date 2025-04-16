import pandas as pd
from ydata_profiling import ProfileReport

# 创建示例 DataFrame
df = pd.read_excel("source/基本信息整理.xlsx", sheet_name="基本信息")

# 生成数据探查报告
profile = ProfileReport(df, title="示例数据探查报告")

# 将报告保存为 HTML 文件
profile.to_file("report.html")
