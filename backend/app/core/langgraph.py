from typing import Dict, Any
from langgraph.graph import StateGraph, END

# Define the state for our graph
class AgentState(Dict[str, Any]):
    message: str
    response: str

# Mock node function for chat
def chat_node(state: AgentState) -> AgentState:
    # In Phase 1, we just return a mock response
    state["response"] = f"Mock response to: {state['message']}"
    return state

# Define the graph
def create_langgraph_app():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("chat", chat_node)
    
    # Set entry point
    workflow.set_entry_point("chat")
    
    # Add edge to end
    workflow.add_edge("chat", END)
    
    # Compile the graph
    app = workflow.compile()
    return app

# Create the app instance
langgraph_app = create_langgraph_app()