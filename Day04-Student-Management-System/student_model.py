
from typing import Tuple, Optional, Dict, Any
import numpy as np
from sklearn.linear_model import LogisticRegression

from student_analytics import to_df, add_features


FEATURE_COLS = ["attendance", "math", "english", "science"]


def train_pass_model(students: list) -> Tuple[Optional[LogisticRegression], Dict[str, Any]]:
    """
    训练“是否及格(pass_flag)”模型
    返回：model, info
    """
    df = to_df(students)
    if df.empty:
        return None, {"error": "暂无数据"}

    df = add_features(df)

    # 训练标签：是否及格
    y = df["pass_flag"].astype(int)  # True/False -> 1/0

    X = df[FEATURE_COLS]

    # 逻辑回归：小数据也能跑；max_iter 给大一点避免不收敛
    model = LogisticRegression(max_iter=2000)
    model.fit(X, y)

    return model, {"features": FEATURE_COLS}


def predict_fail_prob(model: LogisticRegression, student: dict) -> float:
    """
    预测单个学生“不及格概率”
    """
    # 从 dict 取特征
    x = []
    for c in FEATURE_COLS:
        x.append(student.get(c, None))

    # 如果有缺失，直接返回 NaN（你的数据目前很干净，正常不会发生）
    if any(v is None for v in x):
        return float("nan")

    X_one = np.array([x], dtype=float)

    # predict_proba 返回 [P(class=0), P(class=1)]，但我们 y 用 1=pass，所以：
    # P(pass) 在索引 1，P(fail)=1-P(pass)
    p_pass = float(model.predict_proba(X_one)[0, 1])
    p_fail = 1.0 - p_pass
    return p_fail
