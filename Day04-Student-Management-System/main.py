from student_manager import StudentManager


def main():
    manager = StudentManager()
    manager.import_from_csv()
    while True:
        print("\n=== 学生管理系统 (Day6) ===")
        print(f"目前共有 {manager.count()} 名学生已录入")
        print("1. 添加学生")
        print("2. 查看学生")
        print("3. 查找学生")
        print("4. 删除学生")
        print("5. 导出 CSV")
        print("6. 年龄分布统计（Pandas）")
        print("7. 年龄最大 Top5（Pandas）")
        print("8. 汇总信息（Pandas）")
        print("9. 数据分析 KPI（Pandas）")
        print("10. 风险预警名单（Pandas）,含原因")
        print("11. 学生画像报告（按编号）（Pandas）")
        print("12. 数据质量检查（Pandas）")
        print("13. 模型风险 Top10（不及格概率）")
        print("14. 决策冲突检测（规则 vs 模型）")
        print("15. 退出")
        
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
            manager.show_age_stats()
        elif choice == "7":
            manager.show_top_oldest(5)
        elif choice == "8":
            manager.show_summary()
        elif choice == "9":
            manager.show_kpi_summary()
        elif choice == "10":
            manager.show_risk_report()
        elif choice == "11":
            manager.show_student_profile()
        elif choice == "12":
            manager.show_data_quality()
        elif choice == "13":
            manager.show_model_risk_topn(10)  
        elif choice == "14":
            manager.show_conflicts(high_prob=0.6, low_prob=0.1, top_k=20)  
        
        elif choice == "15":
            print("程序结束")
            break
        else:
            print("输入错误，请重新选择")


if __name__ == "__main__":
    main()