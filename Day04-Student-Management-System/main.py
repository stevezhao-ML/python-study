from student_manager import StudentManager

def main():
    manager = StudentManager()
    while True:
        print("\n=== 学生管理系统 (Day4) ===")
        print(f"目前共有 {manager.count()} 名学生已录入")
        print("1. 添加学生")
        print("2. 查看学生")
        print("3. 查找学生")
        print("4. 删除学生")
        print("5. 导出 CSV")
        print("6. 退出")
        
        choice = input("请选择功能：").strip()

        if choice == "1":
            manager.add_student()     
        elif choice == "2":
            manager.show_students()
        elif choice == "3":
            manager.find_students()
        elif choice == "4":
            manager.delete_student()
        elif choice == "5":
            manager.export_csv()
        elif choice == "6":
            print("程序结束")
            break
        else:
            print("输入错误，请重新选择")


if __name__ == "__main__":
    main()