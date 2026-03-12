from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    user_text: str
    response: str
    messages: Annotated[list, add_messages]  # LangGraph maneja el historial aquí