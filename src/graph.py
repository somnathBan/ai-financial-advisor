from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import ingestion_node, strategy_node, reasoning_node # Add the 3rd node

# 1. Initialize
workflow = StateGraph(AgentState)

# 2. Register Nodes
workflow.add_node("ingest", ingestion_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("reasoning", reasoning_node) # Add this

# 3. Connect the Flow
workflow.set_entry_point("ingest")
workflow.add_edge("ingest", "strategy")
workflow.add_edge("strategy", "reasoning") # Connect Strategy to Reasoning
workflow.add_edge("reasoning", END)        # Reasoning is the finish line

# 4. Compile
app_brain = workflow.compile()