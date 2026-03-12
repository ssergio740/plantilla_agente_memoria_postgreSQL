from langgraph.graph import StateGraph, START, END
from worker.agent.state import AgentState
from worker.agent.nodes import generate_response, should_use_tools, tool_node
from worker.agent.tools import ALL_TOOLS


def build_graph(checkpointer):
    builder = StateGraph(AgentState)

    builder.add_node("generate_response", generate_response)

    if ALL_TOOLS:
        # Con tools: routing condicional
        builder.add_node("tools", tool_node)
        builder.add_edge(START, "generate_response")
        builder.add_conditional_edges(
            "generate_response",
            should_use_tools,
            {"tools": "tools", "end": END},
        )
        builder.add_edge("tools", "generate_response")
    else:
        # Sin tools: flujo directo
        builder.add_edge(START, "generate_response")
        builder.add_edge("generate_response", END)

    return builder.compile(checkpointer=checkpointer)


async def run_agent(graph, user_text: str, phone_number: str) -> str:
    config = {"configurable": {"thread_id": phone_number}}
    final_state = await graph.ainvoke(
        {"user_text": user_text, "response": "", "messages": []},
        config=config,
    )
    return final_state["response"]