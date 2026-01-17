import json
import csv
import os

class StudentManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_file = os.path.join(self.base_dir, "students.json")
        self.csv_file  = os.path.join(self.base_dir, "students_in_d3.csv")
        self.students = self.load_students()
        
    def export_csv(self):
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:   # !!!!!!!f,w,r
            writer = csv.DictWriter(f, fieldnames=["name", "age"])
            writer.writeheader()
            writer.writerows(self.students)
        print(f"已导出 CSV 文件：{self.csv_file}")
        
    def load_students(self):
        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_students(self):
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.students, f, indent=2, ensure_ascii=False)  # !!!!!!!
    
    def count(self):
        return len(self.students)
    
    def add_student(self):
        while True:
            name = input("请输入学生姓名：").strip()
            if not name:
                print("名字不能为空，请重新输入：")
                continue            
            age = input("请输入学生年龄：").strip()
            if not age.isdigit():
                print("年龄必须为整数，请重新输入：")
                continue
            
            self.students.append({"name": name, "age": int(age)})
            self.save_students()
            print(f"{name} 添加成功！")
            break
        
    def show_students(self): 
        if not self.students:
            print("暂无学生数据")
            return
        name_width = max(len(s["name"]) for s in self.students) 
        print(f"{'编号':<5} {'姓名':<{name_width}} {'年龄':<4}")  
        for i, v in enumerate(self.students):
            print(f"{i+1:<7} {v['name']:<{name_width + 2}} {v['age']:<4}")

    def find_students(self):         
        find_name = input("请输入要查找的人的姓名：").strip()
        found_name = [s for s in self.students if find_name.lower() in s["name"].lower()]
        if found_name:
            name_width = max(len(s["name"]) for s in found_name) 
            print(f"{'姓名':<{name_width}} {'年龄':<4}") 
            for s in found_name:
                
                print(f"{s['name']:<{name_width + 3}}{s['age']:<4}")
            print("一共找到", len(found_name), "位，查询完毕！！！")
        else:
            print("未找到该学生")

    def delete_student(self):
        if not self.students:
            print("暂无学生数据，无法删除")
            return
        self.show_students()
        index = input("请输入要删除的学生编号：")
        if not index.isdigit():
            print("请输入数字")
            return
        index = int(index) - 1
        if 0 <= index < len(self.students):
            double_check1 = input(f"确认删除请按'y'，否则按任意键取消！将删除编号为 {index+1} 的同学数据：").strip()
            if double_check1.lower() == 'y':
                removed = self.students.pop(index)
                self.save_students()
                print(f"{removed['name']} 已删除")
            else:
                print("删除操作已取消！")
        else:
            print("编号错误")