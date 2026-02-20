from dataclasses import dataclass
from typing import Any, Dict, Optional

RANK = {"低风险": 0, "中风险": 1, "高风险": 2}

@dataclass
class DecisionConfig:
    # 模型阈值（可调策略参数）
    high_prob: float = 0.60   # 模型认为“高风险”的阈值
    low_prob: float = 0.10    # 模型认为“很安全”的阈值

    # 是否走“安全优先”（冲突时更倾向升风险）
    safety_first: bool = True


class DecisionEngine:
    def __init__(self, config: Optional[DecisionConfig] = None):
        self.cfg = config or DecisionConfig()

    def evaluate(self, profile: Dict[str, Any], p_fail: Optional[float], model_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        输入：
        - profile：来自 analytics 的画像（含 risk_level, reason, avg_score, attendance 等）
        - p_fail：模型不及格概率（可能 None）
        - model_info：模型元信息（可选，用于审计）

        输出：
        - final_risk_level
        - decision_action
        - reasons（可解释）
        - audit（可审计）
        """
        rule_level = str(profile.get("risk_level", ""))
        rule_rank = RANK.get(rule_level, -1)

        reasons = []
        audit = {
            "rule_level": rule_level,
            "p_fail": p_fail,
            "thresholds": {
                "high_prob": self.cfg.high_prob,
                "low_prob": self.cfg.low_prob,
            },
            "model": model_info or {},
        }

        # 规则原因（你 analytics 已经提供了）
        rule_reason = profile.get("reason")
        if rule_reason:
            reasons.append(f"规则判断：{rule_level}（{rule_reason}）")
        else:
            reasons.append(f"规则判断：{rule_level}")

        # 没有模型就只用规则
        if p_fail is None:
            final_level = rule_level or "未知"
            action = self._action(final_level)
            return {
                "final_risk_level": final_level,
                "decision_action": action,
                "reasons": reasons + ["模型未就绪或特征缺失，未参与裁决"],
                "audit": audit,
            }

        # 模型解释
        reasons.append(f"模型判断：P(fail)={p_fail*100:.1f}%")

        # 模型等级
        if p_fail >= self.cfg.high_prob:
            model_rank = 2
            model_level = "高风险"
        elif p_fail <= self.cfg.low_prob:
            model_rank = 0
            model_level = "低风险"
        else:
            model_rank = 1
            model_level = "中风险"

        reasons.append(f"模型映射等级：{model_level}（阈值：≥{self.cfg.high_prob:.0%} 为高，≤{self.cfg.low_prob:.0%} 为低）")

        # ✅ 裁决策略
        if self.cfg.safety_first:
            # 安全优先：取更高风险（更保守）
            final_rank = max(rule_rank, model_rank)
        else:
            # 非保守：取平均（可换成别的策略）
            final_rank = int(round((rule_rank + model_rank) / 2))

        final_level = [k for k, v in RANK.items() if v == final_rank][0]
        action = self._action(final_level)

        # 冲突标记（审计/治理入口）
        if abs(rule_rank - model_rank) >= 2:
            reasons.append("⚠️ 规则与模型存在明显冲突（差异≥2级），建议复核或调参")

        return {
            "final_risk_level": final_level,
            "decision_action": action,
            "reasons": reasons,
            "audit": audit,
        }

    def _action(self, level: str) -> str:
        if level == "高风险":
            return "干预：优先联系家长/辅导；本周复盘出勤与短板科目"
        if level == "中风险":
            return "提醒：每周跟踪小测；关注出勤与短板"
        if level == "低风险":
            return "观察：保持节奏；可考虑拔高训练"
        return "未知：需要补充数据"