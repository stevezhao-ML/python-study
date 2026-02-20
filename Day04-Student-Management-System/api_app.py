from fastapi import FastAPI, HTTPException
from typing import List
from student_manager import StudentManager
from student_analytics import student_profile
from student_model import predict_fail_prob

app = FastAPI(title="Student Risk API", version="0.1")

# 启动时初始化：加载数据 + 训练模型（你现在数据量小，启动很快）
manager = StudentManager()


@app.get("/profile/{idx}")
def get_profile(idx: int):
    result = student_profile(manager.students, idx)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # 模型概率
    model_service = manager.model_service

    if not model_service.is_ready():
        result["model_fail_prob"] = None
    else:
        p_fail = model_service.predict_fail_prob(result)
        if p_fail != p_fail:  # NaN
            result["model_fail_prob"] = None
            result["model_fail_prob_pct"] = None
        else:
            # 原始值保留（可选）
            result["model_fail_prob"] = p_fail
            # 更适合展示的百分比
            pct = p_fail * 100
            if pct < 0.05:
                pct = 0.0
            result["model_fail_prob_pct"] = round(pct, 1)

    # avg_score 保留两位
    if isinstance(result.get("avg_score"), (int, float)):
        result["avg_score"] = round(float(result["avg_score"]), 2)

    return result

@app.get("/profile/by-name/{name}")
def get_profile_by_name(name: str):
    """
    按姓名精确匹配（不区分大小写）
    - 如果重名：返回 409 并提示
    """
    name_key = name.strip().lower()
    matches = []
    for i, s in enumerate(manager.students, start=1):
        n = str(s.get("name", "")).strip().lower()
        if n == name_key:
            matches.append(i)

    if not matches:
        raise HTTPException(status_code=404, detail=f"未找到姓名为 {name!r} 的学生")

    if len(matches) > 1:
        raise HTTPException(
            status_code=409,
            detail=f"发现重名：{name!r} 对应多个编号 {matches}，请用 /profile/{{idx}} 指定编号"
        )

    # 复用已有接口逻辑
    idx = matches[0]
    return get_profile(idx)


@app.get("/profiles/search")
def search_profiles(kw: str, limit: int = 10):
    """
    按姓名模糊搜索（不区分大小写）
    返回：最多 limit 个匹配项（含 idx + name），方便前端做搜索
    """
    kw2 = kw.strip().lower()
    if not kw2:
        return []

    results = []
    for i, s in enumerate(manager.students, start=1):
        n_raw = str(s.get("name", "")).strip()
        if kw2 in n_raw.lower():
            results.append({"idx": i, "name": n_raw})
            if len(results) >= limit:
                break

    return results
