import json
import csv
import os

from typing import Optional
from student_analytics import age_distribution, top_n_oldest, summary, kpi_summary, risk_report, student_profile, risk_report_with_reason
from student_analytics import data_quality_report, profiles, risk_rank
from student_model import train_pass_model, predict_fail_prob
from student_analytics import student_profile
        
class StudentManager:
    def __init__(self):
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_file = os.path.join(self.base_dir, "students.json")
        self.csv_file  = os.path.join(self.base_dir, "students_in_d3.csv")
        self.students = self.load_students()
        for s in self.students:
                s.setdefault("attendance", None)
                s.setdefault("math", None)
                s.setdefault("english", None)
                s.setdefault("science", None)
        self.save_students()
        self.model, self.model_info = train_pass_model(self.students)
        
    def import_from_csv(self):
        """
        从 CSV 导入成绩/出勤，并回写到 students.json
        匹配规则：优先按 name 匹配（如有重名建议以后加 id）
        CSV 需要列名：name, age, attendance, math, english, science
        """
        if not os.path.exists(self.csv_file):
            print(f"找不到 CSV 文件：{self.csv_file}")
            return

        # 建立 name -> student 的索引
        index = {}
        for s in self.students:
            name = str(s.get("name", "")).strip()
            if name:
                index[name] = s

        updated = 0
        skipped = 0

        with open(self.csv_file, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = str(row.get("name", "")).strip()
                if not name or name not in index:
                    skipped += 1
                    continue

                s = index[name]

                # age（可选更新）
                age_raw = str(row.get("age", "")).strip()
                if age_raw.isdigit():
                    s["age"] = int(age_raw)

                # attendance：允许 0.92 / 92% / 92
                att_raw = str(row.get("attendance", "")).strip()
                if att_raw.endswith("%"):
                    att_raw = att_raw[:-1].strip()
                    try:
                        s["attendance"] = float(att_raw) / 100.0
                    except ValueError:
                        s["attendance"] = None
                elif att_raw != "":
                    att_raw = att_raw.replace(",", ".")  # 兼容 0,92
                    try:
                        att_val = float(att_raw)
                        # 如果用户填了 92，当作 92% 处理
                        if att_val > 1:
                            att_val = att_val / 100.0
                        s["attendance"] = att_val
                    except ValueError:
                        s["attendance"] = None

                # 成绩：0~100
                def parse_int(v):
                    v = str(v).strip()
                    if v == "":
                        return None
                    if v.isdigit():
                        return int(v)
                    return None

                s["math"] = parse_int(row.get("math", ""))
                s["english"] = parse_int(row.get("english", ""))
                s["science"] = parse_int(row.get("science", ""))

                updated += 1

        self.save_students()
        print(f"CSV 导入完成：更新 {updated} 条，跳过 {skipped} 条（CSV 中 name 未匹配或为空）。")    
        
    
    def show_age_stats(self):
        stats = age_distribution(self.students)
        if not stats:
            print("暂无数据，无法统计年龄分布")
            return
        print("\n=== 年龄分布 ===")
        for age, cnt in stats.items():
            print(f"{age} 岁: {cnt} 人")

    def show_top_oldest(self, n=5):
        rows = top_n_oldest(self.students, n=n)
        if not rows:
            print("暂无数据，无法统计 Top 年龄")
            return
        print(f"\n=== 年龄最大 Top {n} ===")
        for i, s in enumerate(rows, start=1):
            print(f"{i}. {s.get('name', '')} - {s.get('age', '')} 岁")

    def show_summary(self):
        info = summary(self.students)
        if info.get("count", 0) == 0:
            print("暂无数据")
            return
        print("\n=== 数据汇总 ===")
        print(f"人数: {info['count']}")
        print(f"平均年龄: {info['avg_age']:.2f}")
        print(f"最小年龄: {info['min_age']}")
        print(f"最大年龄: {info['max_age']}")
    
    def _input_int(self, prompt: str, min_v: Optional[int] = None, max_v: Optional[int] = None) -> int:
        while True:
            s = input(prompt).strip()
            if not s.isdigit():
                print("请输入整数。")
                continue
            v = int(s)
            if min_v is not None and v < min_v:
                print(f"不能小于 {min_v}。")
                continue
            if max_v is not None and v > max_v:
                print(f"不能大于 {max_v}。")
                continue
            return v    
    def _input_float(self, prompt: str, min_v: Optional[float] = None, max_v: Optional[float] = None) -> float:
        while True:
            s = input(prompt).strip()
            try:
                v = float(s)
            except ValueError:
                print("请输入数字（可带小数）。")
                continue
            if min_v is not None and v < min_v:
                print(f"不能小于 {min_v}。")
                continue
            if max_v is not None and v > max_v:
                print(f"不能大于 {max_v}。")
                continue
            return v
    def _input_nonempty(self, prompt: str) -> str:
        while True:
            s = input(prompt).strip()
            if not s:
                print("不能为空，请重新输入。")
                continue
            return s
    
    def export_csv(self):
        fieldnames = ["name", "age", "attendance", "math", "english", "science"]
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:   # !!!!!!!f,w,r
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            rows = []
            for s in self.students:
                rows.append({
                    "name": s.get("name", ""),
                    "age": s.get("age", ""),
                    "attendance": s.get("attendance", ""),
                    "math": s.get("math", ""),
                    "english": s.get("english", ""),
                    "science": s.get("science", ""),
                })
            writer.writerows(rows)
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
        name = self._input_nonempty("请输入学生姓名：")
        age = self._input_int("请输入学生年龄：", min_v=1, max_v=120)

        # 出勤率：0~1
        attendance = self._input_float("请输入出勤率（0~1，例如 0.92）：", min_v=0.0, max_v=1.0)

        # 成绩：0~100
        math = self._input_int("请输入数学成绩（0~100）：", min_v=0, max_v=100)
        english = self._input_int("请输入英语成绩（0~100）：", min_v=0, max_v=100)
        science = self._input_int("请输入科学成绩（0~100）：", min_v=0, max_v=100)

        self.students.append({
            "name": name,
            "age": age,
            "attendance": attendance,
            "math": math,
            "english": english,
            "science": science,
        })
        self.save_students()
        print(f"{name} 添加成功！")
        
    def show_kpi_summary(self):
        info = kpi_summary(self.students)
        if info.get("count", 0) == 0:
            print("暂无数据")
            return

        print("\n=== 数据分析 KPI ===")
        print(f"人数: {info['count']}")
        print(f"平均分: {info['avg_score']:.2f}")
        print(f"及格率: {info['pass_rate']*100:.1f}%")
        print(f"高风险人数: {info['high_risk']}")
        print(f"中风险人数: {info['mid_risk']}")

    def show_risk_report(self):
        rows = risk_report_with_reason(self.students)
        if not rows:
            print("暂无风险名单（或暂无数据）")
            return

        print("\n=== 风险预警名单（中/高风险） ===")
        print(f"{'姓名':<10} {'年龄':<4} {'出勤':<6} {'数学':<4} {'英语':<4} {'科学':<4} {'均分':<6} {'风险':<4} {'原因'}")

        for r in rows:
            name = str(r.get("name", ""))
            age = r.get("age", "")
            att = r.get("attendance", "")
            math = r.get("math", "")
            eng = r.get("english", "")
            sci = r.get("science", "")
            avg = r.get("avg_score", "")
            risk = r.get("risk_level", "")
            reason = r.get("reason", "")

            avg_show = f"{avg:.2f}" if isinstance(avg, (int, float)) else str(avg)
            att_show = f"{att:.2f}" if isinstance(att, (int, float)) else str(att)

            print(f"{name:<10} {str(age):<4} {att_show:<6} {str(math):<4} {str(eng):<4} {str(sci):<4} {avg_show:<6} {risk:<4} {reason}")
            
    def show_students(self):
        if not self.students:
            print("暂无学生数据")
            return

        name_width = max(len(str(s.get("name",""))) for s in self.students)
        print(f"{'编号':<5} {'姓名':<{name_width}} {'年龄':<4} {'出勤':<6} {'均分':<6} {'风险':<4}")

        # 为了不在 manager 层写 Pandas，你可以只显示“已有字段”
        for i, s in enumerate(self.students, start=1):
            age = s.get("age", "")
            att = s.get("attendance", "")
            # 这里先不计算均分/风险（那是 analytics 的活），先留空也可以
            att_show = f"{att:.2f}" if isinstance(att, (int, float)) else str(att)
            print(f"{i:<7} {str(s.get('name','')):<{name_width + 2}} {str(age):<4} {att_show:<6} {'':<6} {'':<4}")

    def show_student_profile(self):
        if not self.students:
            print("暂无学生数据")
            return

        # 显示编号供选择（你坚持不在这里算均分/风险没问题）
        self.show_students()

        s = input("请输入要查看画像的学生编号：").strip()
        if not s.isdigit():
            print("请输入数字编号")
            return

        idx = int(s)
        result = student_profile(self.students, idx)
        if "error" in result:
            print(result["error"])
            return

        print("\n=== 学生画像报告 ===")
        print(f"姓名：{result.get('name','')}")
        print(f"年龄：{result.get('age','')}")

        att = result.get("attendance", None)
        att_show = f"{att:.2f}" if isinstance(att, (int, float)) else str(att)
        print(f"出勤率：{att_show}")

        print(f"数学：{result.get('math','')}")
        print(f"英语：{result.get('english','')}")
        print(f"科学：{result.get('science','')}")

        avg = result.get("avg_score", None)
        avg_show = f"{avg:.2f}" if isinstance(avg, (int, float)) else str(avg)
        print(f"均分：{avg_show}")

        print(f"风险等级：{result.get('risk_level','')}")
        print(f"原因：{result.get('reason','')}")
        print(f"建议：{result.get('suggestion','')}")

        # === 模型预测（AI 部分）===
        if self.model is None:
            print("模型预测不及格概率：模型未训练")
            return

        p_fail = predict_fail_prob(self.model, result)
        if p_fail == p_fail:  # NaN 检查
            print(f"模型预测不及格概率：{p_fail*100:.1f}%")
        else:
            print("模型预测不及格概率：无法计算（存在缺失特征）")

        
    
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
    def show_data_quality(self):
        report = data_quality_report(self.students)

        if report.get("count", 0) == 0:
            print("暂无数据")
            return

        print("\n=== 数据质量检查（Pandas）===")
        print(f"总人数：{report['count']}")

        miss = report["missing"]
        inv = report["invalid"]

        print("\n-- 缺失值统计（为空/None/无法解析为数字） --")
        print(f"age 缺失：{miss['age']}")
        print(f"attendance 缺失：{miss['attendance']}")
        print(f"math 缺失：{miss['math']}")
        print(f"english 缺失：{miss['english']}")
        print(f"science 缺失：{miss['science']}")

        print("\n-- 非法范围统计 --")
        print("attendance 合法范围：0~1（或 0~100%）")
        print(f"attendance 非法：{inv['attendance']}")
        print("成绩合法范围：0~100")
        print(f"math 非法：{inv['math']}")
        print(f"english 非法：{inv['english']}")
        print(f"science 非法：{inv['science']}")
        print("age 合法范围：1~120")
        print(f"age 非法：{inv['age']}")

        print("\n-- 原始数据类型分布（帮助定位字符串/None） --")
        td = report["type_dist"]
        for k in ["age", "attendance", "math", "english", "science"]:
            print(f"{k}: {td.get(k, {})}")
            
    def show_model_risk_topn(self, n: int = 10):
        if not self.students:
            print("暂无学生数据")
            return
        if self.model is None:
            print("模型未训练，无法计算概率")
            return

        rows = profiles(self.students)  # analytics 负责算均分/风险等
        if not rows:
            print("暂无数据")
            return

        # 批量算不及格概率
        for r in rows:
            p_fail = predict_fail_prob(self.model, r)
            r["fail_prob"] = p_fail

        # 排序：概率高的在前
        rows.sort(key=lambda x: (x.get("fail_prob", float("nan")) if x.get("fail_prob")==x.get("fail_prob") else -1), reverse=True)

        # 只取前 n
        top = rows[:n]

        print(f"\n=== 模型风险 Top {n}（按不及格概率从高到低）===")
        print(f"{'排名':<4} {'姓名':<12} {'P(fail)':<10} {'规则风险':<6} {'均分':<6} {'出勤':<6}")
        for i, r in enumerate(top, start=1):
            name = str(r.get("name", ""))
            risk = str(r.get("risk_level", ""))
            avg = r.get("avg_score", "")
            att = r.get("attendance", "")
            p = r.get("fail_prob", float("nan"))

            p_show = f"{p*100:.1f}%" if isinstance(p, float) and p == p else "NA"
            avg_show = f"{avg:.2f}" if isinstance(avg, (int, float)) else str(avg)
            att_show = f"{att:.2f}" if isinstance(att, (int, float)) else str(att)

            print(f"{i:<4} {name:<12} {p_show:<10} {risk:<6} {avg_show:<6} {att_show:<6}")
            
    def show_conflicts(self,
                        high_prob: float = 0.6,
                        low_prob: float = 0.1,
                        top_k: int = 20):
        """
        冲突检测：
        - A类：规则低/中，但模型不及格概率很高（>= high_prob） -> 潜在漏判
        - B类：规则高，但模型不及格概率很低（<= low_prob） -> 规则偏严
        """
        if not self.students:
            print("暂无学生数据")
            return
        if self.model is None:
            print("模型未训练，无法进行冲突检测")
            return

        rows = profiles(self.students)  # analytics: 规则风险、均分、出勤等
        if not rows:
            print("暂无数据")
            return

        # 算模型概率
        for r in rows:
            r["fail_prob"] = predict_fail_prob(self.model, r)
            r["risk_rank"] = risk_rank(r.get("risk_level", ""))

        conflicts = []

        for r in rows:
            p = r.get("fail_prob", float("nan"))
            if not (isinstance(p, float) and p == p):
                continue

            rr = r.get("risk_rank", -1)

            # A类：规则不高(低/中)，但模型很高
            if rr <= 1 and p >= high_prob:
                conflicts.append({
                    "type": "潜在漏判(规则偏低)",
                    "name": r.get("name", ""),
                    "risk_level": r.get("risk_level", ""),
                    "p_fail": p,
                    "avg_score": r.get("avg_score", ""),
                    "attendance": r.get("attendance", ""),
                })

            # B类：规则高，但模型很低
            if rr == 2 and p <= low_prob:
                conflicts.append({
                    "type": "规则偏严(模型偏低)",
                    "name": r.get("name", ""),
                    "risk_level": r.get("risk_level", ""),
                    "p_fail": p,
                    "avg_score": r.get("avg_score", ""),
                    "attendance": r.get("attendance", ""),
                })

        if not conflicts:
            print("\n=== 决策冲突检测 ===")
            print("未发现明显冲突（在当前阈值设置下）。")
            print(f"阈值：A类 high_prob≥{high_prob:.0%}；B类 low_prob≤{low_prob:.0%}")
            return

        # 排序：先按冲突类型，再按概率极端程度
        def sort_key(x):
            t = x["type"]
            p = x["p_fail"]
            if t.startswith("潜在漏判"):
                return (0, -p)  # 概率越高越靠前
            else:
                return (1, p)   # 概率越低越靠前

        conflicts.sort(key=sort_key)
        conflicts = conflicts[:top_k]

        print("\n=== 决策冲突检测（规则 vs 模型）===")
        print(f"阈值：A类 high_prob≥{high_prob:.0%}（规则低/中但模型高）")
        print(f"      B类 low_prob≤{low_prob:.0%}（规则高但模型低）\n")
        print(f"{'类型':<18} {'姓名':<12} {'规则风险':<6} {'P(fail)':<8} {'均分':<6} {'出勤':<6}")

        for c in conflicts:
            name = str(c.get("name", ""))
            risk = str(c.get("risk_level", ""))
            p = c.get("p_fail", float("nan"))
            avg = c.get("avg_score", "")
            att = c.get("attendance", "")

            p_show = f"{p*100:.1f}%" if isinstance(p, float) and p == p else "NA"
            avg_show = f"{avg:.2f}" if isinstance(avg, (int, float)) else str(avg)
            att_show = f"{att:.2f}" if isinstance(att, (int, float)) else str(att)

            print(f"{c['type']:<18} {name:<12} {risk:<6} {p_show:<8} {avg_show:<6} {att_show:<6}")
