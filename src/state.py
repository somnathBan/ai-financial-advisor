# src/state.py
from typing import TypedDict
import pandas as pd

class AgentState(TypedDict):
    # Inputs
    age: int
    risk: str
    amount: float
    
    # Internal Data
    universe_data: pd.DataFrame
    
    # Outputs
    portfolio_split: dict
    recommendations_df: pd.DataFrame
    ai_reasoning: str
    actual_model_used: str