from typing import TypedDict, Dict
import pandas as pd

class AgentState(TypedDict):
    age: int
    risk: str
    amount: float
    # The 18-fund universe (6 Equity, 6 Debt, 6 Hybrid)
    top_mf_recommendations: pd.DataFrame 
    # System logic outputs
    portfolio_split: Dict[str, float]
    ai_reasoning: str
    actual_model_used: str