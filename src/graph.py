from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import mf_analysis_node, reasoning_node

workflow = StateGraph(AgentState)
workflow.add_node("analyze", mf_analysis_node)
workflow.add_node("reason", reasoning_node)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "reason")
workflow.add_edge("reason", END)

app_brain = workflow.compile()