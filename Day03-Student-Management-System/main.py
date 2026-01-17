import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_file = os.path.join(BASE_DIR, "students.json")
csv_file  = os.path.join(BASE_DIR, "students_in_d3.csv")
print("数据文件保存路径：", csv_file)
print("数据文件保存路径：", json_file)
def export_csv(students, filename="students_in_d3.csv"):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerows(students)
    print(f"已导出 {filepath}")

def load_students():
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_students(students):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)
        
students = load_students()
        
# ---------- 功能函数 ----------
def add_students(students):
    while True:
        name = input("请输入学生姓名：").strip()
        if not name:
            print("名字不能为空，请重新输入：")
            continue            
        age = input("请输入学生年龄：").strip()
        if not age.isdigit():
            print("年龄必须为整数，请重新输入：")
            continue
        
        students.append({"name": name, "age": int(age)})
        save_students(students)
        print(f"{name} 添加成功！")
        break
    
 # 查看所以学员列表，行数从1开始
def show_students(students): 
    if not students:
        print("暂无学生数据")
        return
    name_width = max(len(s["name"]) for s in students) 
    print(f"{'编号':<5} {'姓名':<{name_width}} {'年龄':<4}")  
    for i, v in enumerate(students):
        print(f"{i+1:<7} {v['name']:<{name_width + 2}} {v['age']:<4}")

def find_students(students): 
    
    find_name = input("请输入要查找的人的姓名：")
    found_name = [s for s in students if find_name.lower() in s["name"].lower()]
    if found_name:
        name_width = max(len(s["name"]) for s in found_name) 
        print(f"{'姓名':<{name_width}} {'年龄':<4}") 
        for s in found_name:
            
            print(f"{s['name']:<{name_width + 3}}{s['age']:<4}")
        print("一共找到", len(found_name), "位，查询完毕！！！")
    else:
        print("未找到该学生")

def delete_student(students):
    show_students(students)
    index = input("请输入要删除的学生编号：")
    if not index.isdigit():
        print("请输入数字")
        return
    index = int(index) - 1
    if 0 <= index < len(students):
        double_check1 = input(f"确认删除请按'y'，否则按任意键取消！将删除编号为 {index+1} 的同学数据：")
        if double_check1.lower() == 'y':
            removed = students.pop(index)
            save_students(students)
            print(f"{removed['name']} 已删除")
        else:
            print("删除失败，删除操作已取消！")
    else:
        print("编号错误")
              

while True:
    print("=== 学生管理系统 ===")
    print("目前共有", len(students) , "名学生已录入")
    print("1. 添加学生")
    print("2. 查看学生")
    print("3. 查找学生")
    print("4. 删除学生")
    print("5. 退出")

    choice = input("请选择功能：")

    if choice == "1":
        print("添加学生功能")
        add_students(students)
    elif choice == "2":
        print("查看学生功能")
        show_students(students)
    elif choice == "3":
        print("查找学生功能")
        find_students(students)
    elif choice == "4":
        print("删除学生功能")
        delete_student(students)
    elif choice == "5":
        print("程序结束")
        break
    else:
        print("输入错误")
        
export_csv(students, filename="students_in_d3.csv") # 导出 CSV
