from typing import Any, Dict, Optional
import pandas as pd
from student_model import train_pass_model

class ModelService:
    def __init__(self):
        self._model = None
        self._model_info: Dict[str, Any] = {}
        self._ready = False
        self._feature_cols = None  # 👈 关键

    def load(self, students: list):
        self._model, self._model_info = train_pass_model(students)
        self._feature_cols = self._model_info.get("features")
        self._ready = self._model is not None and bool(self._feature_cols)

    def is_ready(self) -> bool:
        return self._ready

    def predict_fail_prob(self, profile: dict) -> Optional[float]: # deprecated: only for testing / legacy
        if not self._ready:
            return None

        try:
            # 👇 统一用 DataFrame + 固定列顺序
            row = {c: profile.get(c, None) for c in self._feature_cols}
            if any(v is None for v in row.values()):
                return None

            X = pd.DataFrame([row], columns=self._feature_cols)

            p_pass = float(self._model.predict_proba(X)[0, 1])
            return 1.0 - p_pass

        except Exception:
            return None

    def info(self) -> Dict[str, Any]:
        return self._model_info
