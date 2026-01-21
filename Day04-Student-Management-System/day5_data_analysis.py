import pandas as pd

df = pd.read_csv("students_in_d3.csv")

if df.shape[0] == 0:
    print("没有数据，无法分析")
if "age" in df.columns:
    print("可以做年龄分析")

print(df.shape)
print(df.columns)
print(df.head())

print("最大值是：", df["age"].max())
print("最小值是：", df["age"].min())
print("平均年龄是：", df["age"].mean())

result = (df[df["age"] >= 12].sort_values("age", ascending=False)
    [["name", "age"]])
    
print(result)