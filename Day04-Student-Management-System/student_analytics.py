import pandas as pd

def to_df(students: list) -> pd.DataFrame:
    """list[dict] -> DataFrame，统一入口"""
    if not students:
        return pd.DataFrame()
    return pd.DataFrame(students)

def _clean_age(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗 age：
    - 转成数值（字符串也能转）
    - 非法/缺失变 NaN
    - 去掉缺失 age 的行
    """
    df = df.copy()

    if "age" not in df.columns:
        df["age"] = pd.NA

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df = df.dropna(subset=["age"])
    return df



def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成特征列：
    - avg_score：三科平均
    - pass_flag：是否及格（>=60）
    """
    df = df.copy()

    # 兼容旧数据：缺字段就补 NaN
    for col in ["attendance", "math", "english", "science"]:
        if col not in df.columns:
            df[col] = pd.NA

    # 成绩转数值（防止字符串）
    for col in ["math", "english", "science"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce")

    df["avg_score"] = df[["math", "english", "science"]].mean(axis=1)
    df["pass_flag"] = df["avg_score"] >= 60
    return df

def add_risk_level(df: pd.DataFrame) -> pd.DataFrame:
    """
    风险规则（可解释、偏应用）：
    - 高风险：avg_score < 60 或 attendance < 0.75
    - 中风险：60 <= avg_score < 70 或 attendance < 0.85
    - 低风险：其他
    """
    df = add_features(df).copy()

    # 先默认低风险
    df["risk_level"] = "低风险"

    high = (df["avg_score"] < 60) | (df["attendance"] < 0.75)
    mid = ((df["avg_score"] >= 60) & (df["avg_score"] < 70)) | ((df["attendance"] >= 0.75) & (df["attendance"] < 0.85))

    df.loc[mid, "risk_level"] = "中风险"
    df.loc[high, "risk_level"] = "高风险"

    return df

def risk_report(students: list) -> list:
    """
    输出风险名单（list[dict]），便于系统打印
    """
    df = to_df(students)
    if df.empty:
        return []

    df = add_risk_level(df)
    df2 = df[df["risk_level"].isin(["中风险", "高风险"])].copy()

    # 排序：高风险优先，其次平均分更低、出勤更低
    risk_order = {"高风险": 0, "中风险": 1, "低风险": 2}
    df2["risk_rank"] = df2["risk_level"].map(risk_order)

    df2 = df2.sort_values(["risk_rank", "avg_score", "attendance"], ascending=[True, True, True])

    cols = ["name", "age", "attendance", "math", "english", "science", "avg_score", "risk_level"]
    for c in cols:
        if c not in df2.columns:
            df2[c] = pd.NA

    return df2[cols].to_dict(orient="records")

def kpi_summary(students: list) -> dict:
    """
    KPI 汇总：人数、平均分、及格率、高风险人数、中风险人数
    """
    df = to_df(students)
    if df.empty:
        return {"count": 0}

    df = add_risk_level(df)

    count = int(df.shape[0])
    avg_score = float(df["avg_score"].mean())
    pass_rate = float(df["pass_flag"].mean())  # True/False 的平均值就是比例

    high_cnt = int((df["risk_level"] == "高风险").sum())
    mid_cnt = int((df["risk_level"] == "中风险").sum())

    return {
        "count": count,
        "avg_score": avg_score,
        "pass_rate": pass_rate,
        "high_risk": high_cnt,
        "mid_risk": mid_cnt,
    }

def age_distribution(students: list) -> dict:
    """
    年龄分布统计：{年龄: 人数}
    """
    df = to_df(students)
    if df.empty:
        return {}

    df = _clean_age(df)
    if df.empty:
        return {}

    # 先转 int，保证 sort_index 可靠
    ages = df["age"].astype(int)
    return ages.value_counts().sort_index().to_dict()

def top_n_oldest(students: list, n: int = 5) -> list:
    """
    年龄最大 Top N：返回 list[dict]
    """
    df = to_df(students)
    if df.empty:
        return []

    df = _clean_age(df)
    if df.empty:
        return []

    df["age"] = df["age"].astype(int)
    df2 = df.sort_values("age", ascending=False).head(n)
    return df2.to_dict(orient="records")

def summary(students: list) -> dict:
    """
    汇总信息：人数、平均年龄、最小/最大年龄
    """
    df = to_df(students)
    if df.empty:
        return {"count": 0}

    df = _clean_age(df)
    if df.empty:
        return {"count": 0}

    df["age"] = df["age"].astype(int)

    return {
        "count": int(df.shape[0]),
        "avg_age": float(df["age"].mean()),
        "min_age": int(df["age"].min()),
        "max_age": int(df["age"].max()),
    }
def _safe_float(x):
    return x if isinstance(x, (int, float)) else None

def _fmt(x, nd=2):
    if isinstance(x, (int, float)):
        return f"{x:.{nd}f}"
    return str(x)

def explain_row(row: dict) -> str:
    """
    给单个学生生成风险原因解释（可读文本）
    依赖字段：avg_score, attendance, math/english/science, risk_level
    """
    reasons = []

    avg = row.get("avg_score", None)
    att = row.get("attendance", None)

    avg_f = _safe_float(avg)
    att_f = _safe_float(att)

    # 规则原因（跟你 risk_level 规则一致）
    if avg_f is not None:
        if avg_f < 60:
            reasons.append(f"均分{_fmt(avg_f)}低于60")
        elif avg_f < 70:
            reasons.append(f"均分{_fmt(avg_f)}偏低(60-70)")
    else:
        reasons.append("均分缺失")

    if att_f is not None:
        if att_f < 0.75:
            reasons.append(f"出勤{_fmt(att_f)}低于0.75")
        elif att_f < 0.85:
            reasons.append(f"出勤{_fmt(att_f)}偏低(0.75-0.85)")
    else:
        reasons.append("出勤缺失")

    # 找短板科目
    scores = {}
    for k in ["math", "english", "science"]:
        v = row.get(k, None)
        v_f = _safe_float(v)
        if v_f is not None:
            scores[k] = v_f

    if scores:
        worst_subj = min(scores, key=scores.get)
        worst_score = scores[worst_subj]
        name_map = {"math": "数学", "english": "英语", "science": "科学"}
        reasons.append(f"短板科目：{name_map.get(worst_subj, worst_subj)}({_fmt(worst_score, nd=0)})")

    # 合并
    return "；".join(reasons)


def risk_report_with_reason(students: list) -> list:
    """
    风险名单 + 原因（reason）
    """
    rows = risk_report(students)
    if not rows:
        return []

    for r in rows:
        r["reason"] = explain_row(r)
    return rows


def student_profile(students: list, index_1based: int) -> dict:
    """
    学生画像（按编号：1 开始）
    返回 dict，给 manager 打印用
    """
    if index_1based <= 0 or index_1based > len(students):
        return {"error": "编号超出范围"}

    df = to_df(students)
    if df.empty:
        return {"error": "暂无数据"}

    # 生成特征+风险
    df = add_risk_level(df)

    # 取出对应行
    i = index_1based - 1
    row = df.iloc[i].to_dict()

    # 计算短板科目
    scores = {}
    for k in ["math", "english", "science"]:
        v = row.get(k, None)
        v = pd.to_numeric(v, errors="coerce")
        if pd.notna(v):
            scores[k] = float(v)

    name_map = {"math": "数学", "english": "英语", "science": "科学"}
    weakest = None
    if scores:
        wk = min(scores, key=scores.get)
        weakest = {"subject": name_map.get(wk, wk), "score": scores[wk]}

    profile = {
        "name": row.get("name", ""),
        "age": row.get("age", ""),
        "attendance": row.get("attendance", None),
        "math": row.get("math", None),
        "english": row.get("english", None),
        "science": row.get("science", None),
        "avg_score": row.get("avg_score", None),
        "pass_flag": row.get("pass_flag", None),
        "risk_level": row.get("risk_level", ""),
        "reason": explain_row(row),
        "weakest": weakest,
        "suggestion": None,
    }

    # 建议动作（简单可解释）
    if profile["risk_level"] == "高风险":
        profile["suggestion"] = "建议：优先补短板科目 + 提升出勤；本周内安排一次家校/辅导沟通。"
    elif profile["risk_level"] == "中风险":
        profile["suggestion"] = "建议：巩固薄弱科目；保持出勤稳定；每周一次小测跟踪。"
    else:
        profile["suggestion"] = "建议：保持当前节奏；可尝试拔高训练或竞赛拓展。"

    return profile    

def data_quality_report(students: list) -> dict:
    """
    数据质量检查（用于排查 NaN/脏数据）
    返回 dict，给 manager 打印使用
    检查内容：
    - 缺失：attendance / math / english / science
    - 非法范围：attendance 不在 0~1，成绩不在 0~100
    - 列类型分布：帮助定位字符串/None 等
    """
    df = to_df(students)
    if df.empty:
        return {"count": 0}

    # 确保列存在
    cols = ["attendance", "math", "english", "science", "age", "name"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA

    # 解析 attendance：允许 "92%" / "92" / "0.92" / "0,92"
    att_raw = df["attendance"].astype(str).str.strip()
    att_raw = att_raw.replace({"None": "", "nan": "", "NaN": ""})

    # 去掉百分号
    has_pct = att_raw.str.endswith("%")
    att_num = att_raw.str.replace("%", "", regex=False)

    # 逗号小数转点
    att_num = att_num.str.replace(",", ".", regex=False)

    att_val = pd.to_numeric(att_num, errors="coerce")
    # 如果是百分号或大于1，当作百分数处理（92 -> 0.92）
    att_val = att_val.where(~(has_pct | (att_val > 1)), att_val / 100.0)

    # 解析成绩：强制数值化
    score_cols = ["math", "english", "science"]
    score_vals = {}
    for c in score_cols:
        score_vals[c] = pd.to_numeric(df[c], errors="coerce")

    # 缺失统计
    missing_attendance = int(att_val.isna().sum())
    missing_scores = {c: int(score_vals[c].isna().sum()) for c in score_cols}

    # 非法范围统计
    invalid_attendance = int(((att_val < 0) | (att_val > 1)).sum(skipna=True))
    invalid_scores = {
        c: int(((score_vals[c] < 0) | (score_vals[c] > 100)).sum(skipna=True))
        for c in score_cols
    }

    # 年龄简单检查（可选）
    age_val = pd.to_numeric(df["age"], errors="coerce")
    missing_age = int(age_val.isna().sum())
    invalid_age = int(((age_val < 1) | (age_val > 120)).sum(skipna=True))

    # 类型分布（帮助你判断是不是有字符串混入）
    type_dist = {}
    for c in ["age", "attendance", "math", "english", "science"]:
        # 原始列（未清洗）类型分布
        type_dist[c] = df[c].map(lambda x: type(x).__name__).value_counts().to_dict()

    return {
        "count": int(df.shape[0]),
        "missing": {
            "age": missing_age,
            "attendance": missing_attendance,
            **missing_scores,
        },
        "invalid": {
            "age": invalid_age,
            "attendance": invalid_attendance,
            **invalid_scores,
        },
        "type_dist": type_dist,
    }
    
def profiles(students: list) -> list:
    """
    给所有学生生成画像所需的字段（含 avg_score, risk_level 等）
    返回 list[dict]，供模型批量预测使用（manager 不碰 pandas）
    """
    df = to_df(students)
    if df.empty:
        return []
    df = add_risk_level(df)
    cols = ["name", "age", "attendance", "math", "english", "science", "avg_score", "risk_level"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols].to_dict(orient="records")

def risk_rank(risk_level: str) -> int:
    """
    风险等级转成数值，便于比较：
    高风险=2，中风险=1，低风险=0
    """
    mapping = {"低风险": 0, "中风险": 1, "高风险": 2}
    return mapping.get(str(risk_level), -1)
